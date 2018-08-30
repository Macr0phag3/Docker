# -*- coding:utf-8 -*-
import docker
import psutil
import traceback
import json
import commands as cmd
import time

"""
1. 返回值 json 说明：
{
    "code": 0, #正确 0，出错 1
    "msg": "", #出错原因
    "result": 其他 #结果
}

2. 以下函数返回值示例均写成 dict
3. 接收返回值的时候注意将 json 转回 dict
"""


def log(msg, level, description, path="./"):  # ok
    """
    记录事件，默认路径为 slave.py 所在路径
    log 文件名为 .slave_log

    参数:
    1. level: 事件等级
    2. description: 事件描述
    3. message: 事件原因的具体描述
    4. path: log 文件的路径; 可选; 默认为 ./
    """

    with open(path+".slave_log", "a") as fp:
        fp.write("[%s]\nlevel: %s\ndescription: %s\nmessage: %s\n\n" %
                 (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), level, description.encode("utf8"), msg))


def ip_used_ls(subnet):
    """
    列出已经被容器占用的 ip（当然，不包含虚拟机自身 ip）

    参数
    1. subnet: ip 所处的网段

    返回值示例
    dicts = {
        "code": 0,
        "msg": "",
        "result": [
                    '192.168.12.123',
                    '192.168.12.111',
                    '192.168.12.134'
                    ]
    }
    """

    dicts = {
        "code": 1,
        "msg": "",
        "result": []
    }

    client = docker.APIClient(base_url='unix://var/run/docker.sock')
    networks = client.networks()
    result = [i["Id"] for i in networks if i["Driver"] ==
              "bridge" and i["IPAM"]["Config"][0]["Subnet"] == subnet]

    if len(result) == 1:
        ID = result[0]
        net = client.inspect_network(ID)
        containers = net["Containers"]
        dicts["result"] = [containers[i]["IPv4Address"].split("/")[0] for i in containers]
        dicts["code"] = 0
    else:
        dicts["msg"] = {
            0: "slave 的 docker 不存在此网段",
            1: "网桥出现重复的问题",
        }[len(result) == 0]

    return json.dumps(dicts)


def run(image_name, ip, nk_name="containers"):  #
    """
    拉起一个容器

    参数
    1. image_name: 镜像的名字
    2. ip: 分配给镜像的 ip
    3. nk_name: 负责桥接的网络的名字，与桥接时创建的名字一致；默认为containers

    返回值示例
    dicts = {
        "code": 0,
        "msg": "",
        "result": {
            "ip": "192.168.12.121",
            "id": "326925f79873ea6a5fbf2b3e112734c697b9c6175798b2466f623f8712d41002"
        }
    }
    """

    dicts = {
        "code": 1,
        "msg": "",
        "result": {}
    }

    try:
        client = docker.APIClient(base_url='unix://var/run/docker.sock')
        networking_config = client.create_networking_config(
            {nk_name: client.create_endpoint_config(
                ipv4_address=ip)})

        con_ready = client.create_container(
            image_name, stdin_open=True, command="/bin/sh",
            detach=True, tty=True, networking_config=networking_config
        )  # 保证容器不会运行后立刻退出的必要可选参数

        id = con_ready.get('Id')
        client.start(container=id)
        dicts["code"] = 0
        dicts["result"]["ip"] = ip
        dicts["result"]["id"] = id

    except Exception, e:
        log(traceback.format_exc(), level="error",
            description="run a container: %s: %s failed" % (image_name, ip))

        dicts["msg"] = str(e)

    return json.dumps(dicts)


def others_cmd(id_or_name, command):  # ok
    """
    除了 run 的其他操作：暂停，恢复，停止，删除(删除前需要停止)，净化（删除所有已经停止的容器）

    参数
    1. id_or_name: 容器的 id 或者 名字
    2. command: 具体命令

    返回值示例
    dicts = {
        "code": 0,
        "msg": "",
        "result": ""
    }
    """

    dicts = {
        "code": 1,
        "msg": "",
        "result": ""
    }

    client = docker.from_env()
    try:
        container = client.containers.get(id_or_name)
    except Exception, e:
        log(traceback.format_exc(), level="error",
            description="no such container: %s" % (id_or_name))

        dicts["msg"] = str(e)
        return json.dumps(dicts)

    commands = {
        "pause": container.pause,
        "unpause": container.unpause,
        "kill":  container.kill,
        "rm":  container.remove,
    }

    try:
        commands[command]()
        dicts["code"] = 0
    except Exception, e:
        log(traceback.format_exc(), level="error",
            description="%s the container %s failed" % (command, id_or_name))

        dicts["msg"] = str(e)

    return json.dumps(dicts)


def containers_ls():  # ok
    """
    列出所有容器

    返回值示例
    dicts = {
        "code": 0,
        "msg": "",
        "result": [
            {
                "id": "326925f79873ea6a5fbf2b3e112734c697b9c6175798b2466f623f8712d41002",
                "status": "running",
                "ip": "192.168.12.67",
                "image name": "image_name"
            },
            {
                "id": "20014d2178f326f6642b8975716c9b796c437211e3b2fbf5a6ae37897f529623",
                "status": "paused",
                "ip": "192.168.12.137",
                "image name": "image_name"
            }
        ]
    }
    """

    dicts = {
        "code": 1,
        "msg": "",
        "result": []
    }

    try:
        client = docker.APIClient(base_url='unix://var/run/docker.sock')
        for i, container in enumerate(client.containers(all=True)):
            if container["NetworkSettings"]["Networks"].has_key("containers"):
                container_ip = container["NetworkSettings"]["Networks"]["containers"]["IPAMConfig"]["IPv4Address"]
            else:
                container_ip = "out of the subnet"

            dicts["result"].append({
                "id": container["Id"],
                "status": container["State"],
                "ip": container_ip,
                "image name": container["Image"]
            })

        dicts["code"] = 0

    except Exception, e:
        log(traceback.format_exc(), level="error",
            description="get all containers failed")

        dicts["msg"] = str(e)

    return json.dumps(dicts)


def load_ls():  # ok
    """
    查询负载情况

    返回值示例
    dicts = {
        "code": 0,
        "msg": "",
        "result": {
            "cpu": 1.0,
            "mem": 12.1
        }
    }
    """

    dicts = {
        "code": 1,
        "msg": "",
        "result": {}
    }

    try:
        dicts["result"]["cpu"] = psutil.cpu_percent(interval=0.1, percpu=False)
        dicts["result"]["mem"] = psutil.virtual_memory().percent
        dicts["code"] = 0
    except Exception, e:
        log(traceback.format_exc(), level="error",
            description="get loads failed")

        dicts["msg"] = str(e)

    return json.dumps(dicts)


def nk_bridge(subnet, raw_ip, iface, gateway, nk_name='containers'):
    """
    将docker与宿主机桥接起来

    参数
    1. subnet: docker 拉起容器后，容器期望所处的子网。格式为: xx.xx.xx.xx/xx
    2. raw_ip: 为网卡（如 ens33）的原 ip 地址，并非网关地址
    3. iface: 桥接所使用的网卡
    4. gateway: 网关地址
    5. nk_name: 可选参数；为新建网络的名字

    返回值示例
    dicts = {
        "code": 0,
        "msg": "",
        "result": ""
    }
    """

    dicts = {
        "code": 1,
        "msg": "",
        "result": ""
    }

    client = docker.APIClient(base_url='unix://var/run/docker.sock')
    ipam_pool = docker.types.IPAMPool(
        subnet=subnet,
        gateway=raw_ip
    )

    ipam_config = docker.types.IPAMConfig(
        pool_configs=[ipam_pool]
    )

    try:
        client.create_network(nk_name, driver="bridge",
                              ipam=ipam_config)
        status, err = cmd.getstatusoutput("""
iface=$(ifconfig | grep -o "br-[0-9a-z]*");\
ip addr add %s/32 dev $iface;\
ip addr del %s/32 dev %s;\
brctl addif $iface %s;\
ip route del default;\
ip route add default via %s dev $iface""" % (raw_ip, raw_ip, iface, iface, gateway))

        if status:
            log(err, level="error", description="bridge network failed")
            dicts["msg"] = err
        else:
            dicts["code"] = 0

    except Exception, e:
        log(traceback.format_exc(), level="error",
            description="create network failed")

        dicts["msg"] = str(e)

    return json.dumps(dicts)


def images_ls():  # ok
    """
    列出所有镜像

    返回值示例
    dicts = {
        "code": 1,
        "msg": "",
        "result": [
            "image_name_1",
            "image_name_2"
        ]
    }
    """

    dicts = {
        "code": 1,
        "msg": "",
        "result": []
    }

    try:
        client = docker.from_env()
        dicts["result"] = [i.tags[0] for i in client.images.list()]
        dicts["code"] = 0
    except Exception, e:
        log(traceback.format_exc(), level="error",
            description="get all images failed")

        dicts["msg"] = str(e)

    return json.dumps(dicts)


def nk_unbridge(nk_name='containers'):
    """
    取消桥接

    参数
    1. nk_name: 桥接网络时，创建的网络的名字; 可选; 默认为 containers

    返回值示例
    dicts = {
        "code": 0,
        "msg": "",
        "result": ""
    }
    """

    dicts = {
        "code": 1,
        "msg": "",
        "result": ""
    }

    status, err = cmd.getstatusoutput("""
docker network rm %s;
systemctl restart network""" % (nk_name))

    if status:
        log(err, level="error", description="unbridge network failed")
        dicts["msg"] = err
    else:
        dicts["code"] = 0

    return json.dumps(dicts)


def check_alive():
    """
    检查网络情况

    返回值示例
    dicts = {
        "code": 0,
        "msg": "",
        "result": ""
    }
    """

    dicts = {
        "code": 0,
        "msg": "",
        "result": "curl to ip.cn failed"
    }

    for t in range(3):
        if cmd.getstatusoutput("ping -c 5 -i 0.1 -w 1 baidu.com")[0] == 0:
            dicts["result"] = ""
            break

    return json.dumps(dicts)