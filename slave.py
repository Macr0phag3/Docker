# -*- coding:utf-8 -*-
import socket
from toolboxs import stoolbox as st
from toolboxs import ptoolbox as pt
import json
import traceback
import time


def sign_in(ckey):  # ok
    """
    认证接入是否合法

    参数
    1. ckey: 密钥

    返回值示例
    True
    """

    skey = "hack it and docker it!"
    return skey == ckey


def recvd_cmd(mission):
    """
    处理 master 发来的任务，具体负责任务的转发与结果的返回

    参数
    1. mission: master 发来的任务

    返回值
    stoolbox.py 中的各个函数中的返回值
    （原样返回，不做任何处理）
    """

    commands = mission["mission"]  # 具体指令
    if commands == "cmd2slave":
        return st.cmd2slave(mission["commands"])

    elif commands == "cmd2docker":
        return st.cmd2docker(mission["commands"])

    elif commands == "reload":  # 重新载入模块 stoolbox，无需重启 slave
        dicts = {
            "code": 1,
            "msg": "",
            "result": ""
        }

        try:
            reload(st)
            dicts["code"] = 0
        except Exception, e:
            print pt.put_color(u"重新载入模块: stoolbox 失败\n  [-]"+str(e), "red")
            print "-"*50
            pt.log(traceback.format_exc(), level="error",
                   description="%s reload module stoolbox failed" % setting["bridge"]["self_ip"], path=".slave_log")
            dicts["msg"] = str(e)

        return json.dumps(dicts)

    else:
        print pt.put_color(u"无法执行此任务: %s" % commands, "red")
        return json.dumps({
            "code": 1,
            "msg": "This mission: commands is out of slave's ability...",
            "result": ""
        })


def recvd_msg(conn):  # ok
    """
    处理 master 发来的消息，根据任务的数据类型（dict 与 list）
    选择不同的处理方式与返回。
    具体任务由 stoolbox.py 中的函数完成

    参数
    1. conn: 建立起的通道

    {
        "mission": "cmd2slave",
        "commands": {
            "command": "",
            "arg": []
        }
    }
    """

    msg = conn.recv(1024)

    if not msg:  # 空消息，直接舍弃
        return

    mission = json.loads(msg)

    if type(mission) == dict:  # 单任务模式
        recvd_cmd(mission)

    elif type(mission) == list:  # 多任务模式
        results = json.dumps([json.loads(recvd_cmd(mission)) for m in mission])

    else:
        results = json.dumps({
            "code": 1,
            "msg": "",
            "result": "mission's type must be dict or list"
        })

    conn.sendall(results)


"""
监听端口，负责建立通信

1. ip: 允许接入的 ip；默认为 0.0.0.0, 即任意 ip
2. port: 监听的端口; 可选参数; 默认为 1122
"""

ip = '0.0.0.0'
port = 1122
sk = socket.socket()
sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sk.bind((ip, port))
sk.listen(1)

print pt.put_color('slave is online', "green")

while 1:
    try:
        conn, from_ip = sk.accept()
        client_data = conn.recv(1024)
        if sign_in(client_data):
            conn.sendall('hello, my master')
            try:
                recvd_msg(conn)
            except Exception, e:
                print pt.put_color(u"处理信息时发生问题\n  [-]"+str(e), "red")
                print "-"*50
                pt.log(traceback.format_exc(), level="error", description="slave(%s) recvd mission but can't finish it" %
                       setting["bridge"]["self_ip"], path=".slave_log")

                conn.sendall(json.dumps([{
                    "code": 1,
                    "msg": str(e),
                    "result": "",
                }]))
        else:
            msg = u"来自 %s 的非法访问. silence is gold..." % from_ip
            print pt.put_color(msg, "yellow")
            conn.sendall(msg)
    except Exception, e:
        if "Keyboard" not in str(e):
            print pt.put_color(u"出现一个隐藏问题\n  [-]"+str(e), "red")
            print "-"*50
            pt.log(traceback.format_exc(), level="error",
                   description="slave reported an error", path=".slave_log")

        print pt.put_color('slave is offline', "red")
        break

    conn.close()
