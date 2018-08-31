# -*- coding:utf-8 -*-
import socket
import traceback
import IPy
import random
import socket
import json
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


def log(msg, level, description="None", path="./"):  # ok
    """
    记录事件，默认路径为 slave.py 所在路径
    log 文件名为 .master_log

    参数:
    1. level: 事件等级
    2. description: 事件描述
    3. message: 事件原因的具体描述
    4. path: log 文件的路径; 可选; 默认为 ./
    """

    with open(path+".master_log", "a") as fp:
        fp.write("[%s]\nlevel: %s\ndescription: %s\nmessage: %s\n\n" %
                 (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), level, description.encode("utf8"), msg))


def load_setting(config):  # ok
    """
    返回 .setting 中的配置

    参数
    1. config: 具体配置

    返回值示例
    dicts = {
        "subnet": "192.168.0.0/18",
        "self_ip": "192.168.12.1",
        "iface": "eth0",
        "gateway": "192.168.7.1"
    }
    """

    dicts = {
        "code": 1,
        "msg": "",
        "result": []
    }

    try:
        with open(".setting", "r") as fp:
            dicts["result"] = json.load(fp)[config]
            dicts["code"] = 0
    except Exception, e:
        log(traceback.format_exc(), level="error",
            description="load setting: %s failed!" % (config))

        dicts["msg"] = str(e)

    return json.dumps(dicts)


def ip_used(subnet):  # ok
    """
    查看已经使用过的 ip 地址

    参数
    1. subnet: ip 所处的网段

    返回值示例
    dicts = {
        "code": 0,
        "msg": "",
        "result": [
            "ip1",
            "ip2",
            "ip3",
        ]
    }
    """

    dicts = {
        "code": 1,
        "msg": "",
        "result": []
    }

    mission = {
        "mission": "cmd2slave",
        "commands": {
            "command": "ip_used_ls",
            "arg": [subnet]
        }
    }

    result = json.loads(load_setting("slave_ip"))
    if result["code"]:
        dicts["msg"] = result["msg"]
    else:
        ips = result["result"]
        dicts["result"] = ips[:]
        dicts["code"] = 0

        for ip in ips:
            result = json.loads(command2slave(ip, json.dumps(mission)))
            if result["code"]:
                dicts["msg"] += "get ip from %s failed\n%s\n" % (ip, result["msg"])
                dicts["code"] = 1
            else:
                dicts["result"].extend(result["result"])

    return json.dumps(dicts)


def ip_ls(subnet):  # ok
    """
    返回可用的 ip 列表
    1. subnet: ip 所处的网段

    返回值示例
    dicts = {
        "code": 0,
        "msg": "",
        "result": [
            "ip1",
            "ip2",
            "ip3",
        ]
    }
    """

    dicts = {
        "code": 1,
        "msg": "",
        "result": []
    }

    used_ip = json.loads(ip_used(subnet))

    if used_ip["code"]:
        dicts["msg"] = used_ip["msg"]
    else:
        try:
            ips = [ip.strNormal() for ip in IPy.IP(subnet)]
            dicts["result"] = list(set(ips)-set(used_ip["result"]))
            dicts["code"] = 0
        except Exception, e:
            log(traceback.format_exc(), level="error",
                description="the subnet must be in standard form.")

            dicts["msg"] = " (%s)" % str(e)

    return json.dumps(dicts)


def ip_assign(subnet, ip=0):  # ok
    """
    返回一个可用的 ip
    1. subnet: ip 所处的网段
    2. ip: 是否随机选择; 可选; 若不为0，则必须为一个 ip 地址, 为 0 时由系统随机选择

    返回值示例
    dicts = {
        "code": 0,
        "msg": "",
        "result": "192.168.12.31"
    }
    """

    dicts = {
        "code": 1,
        "msg": "",
        "result": ""
    }

    result = json.loads(ip_ls(subnet))

    if result["code"]:
        dicts["msg"] = result["msg"]
    else:
        ip_unused = result["result"]
        if ip == 0:  # 由系统选择
            if ip_unused:
                dicts["result"] = random.choice(ip_unused)
                dicts["code"] = 0
            else:
                dicts["msg"] = "无剩余 ip 地址"
        else:
            if ip not in ip_unused:
                dicts["msg"] = "ip 地址已被占用"
            else:
                try:
                    if ip in IPy.IP(subnet):
                        dicts["result"] = ip
                        dicts["code"] = 0
                    else:
                        dicts["msg"] = "ip 不在网段 %s 内" % subnet
                except Exception, e:
                    log(traceback.format_exc(), level="error",
                        description="this ip is illegal.")

                    dicts["msg"] = "ip 地址非法"

    return json.dumps(dicts)


def check_load():
    """
    返回所有虚拟机的负载情况 (cpu 与 memory)

    返回值示例:
    dicts = {
        "code": 0,
        "msg": "",
        "result": [
                    {"192.168.1.1": {u'cpu': 4.5, u'mem': 17.3}},
                    {"192.168.1.2": {u'cpu': 0.0, u'mem': 17.3}},
                ]
    }
    """

    dicts = {
        "code": 1,
        "msg": "",
        "result": []
    }

    mission = {
        "mission": "cmd2slave",
        "commands": {
            "command": "load_ls",
            "arg": []
        }
    }

    result = json.loads(load_setting("slave_ip"))
    if result["code"]:
        dicts["msg"] = result["msg"]
    else:
        ips = result["result"]
        dicts["code"] = 0
        for ip in ips:
            result = json.loads(command2slave(ip, json.dumps(mission)))
            if result["code"]:
                dicts["msg"] += "get load from %s failed\n%s\n" % (ip, result["msg"])
                dicts["code"] = 1
            else:
                dicts["result"].append({
                    ip: result["result"]
                })

    return json.dumps(dicts)


def command2slave(ip, mission, port=1100, timeout=60):  # ok
    """
    对 slave 指派任务

    参数
    1. ip: slave 的 ip
    2. mission: 具体任务, 格式如下：
        {
            "mission": "", # 具体的任务
            "commands":
            {
                "command": "", # 具体的命令
                "arg": [],  # 参数列表
            }
        }
    3. port: 与 slave 的通信端口; 可选; 默认为 1100
    4. timeout: 等待 slave 返回的超时时间; 可选; 默认为 60s

    返回值示例
    dicts = {
        "code": 0,
        "msg": "",
        "result": "" # 与 slave 返回的值一致
    }
    """

    dicts = {
        "code": 1,
        "msg": "",
        "result": ""
    }

    socket.setdefaulttimeout(timeout)
    sk = socket.socket()
    for i in range(3):
        try:
            sk.connect((ip, port))
            break
        except Exception, e:
            if i == 2:
                log(traceback.format_exc(), level="error",
                    description="connect to slave: %s:%s failed" % (ip, port))

                dicts["msg"] = "connect to slave: %s:%s failed" % (ip, port)
                return json.dumps(dicts)

    try:
        sk.sendall("xxxxxxxxxx")  # 认证 key
        server_reply = sk.recv(1024)

        if server_reply == "hello, my master":  # 认证成功
            sk.sendall(mission)
            dicts = json.loads(sk.recv(1024000))
            sk.close()
        else:  # 认证失败
            dicts["msg"] = "sign in failed"

    except Exception, e:
        log(traceback.format_exc(), level="error",
            description="send a mission to slave(%s) failed" % (ip))

        dicts["msg"] = "send a mission to slave(%s) failed: %s" % (ip, str(e))

    return json.dumps(dicts)
