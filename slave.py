# -*- coding:utf-8 -*-
import socket
from toolboxs import stoolbox as st
import json
import traceback
import time


def put_color(string, color):  # ok
    colors = {
        "green": "32",
        "red": "31",
        "yellow": "33",
        "white": "37",
        "blue": "36",
    }
    return "\033[40;1;%s;40m%s\033[0m" % (colors[color], string)


def sign_in(ckey):  # ok
    """
    认证接入是否合法

    参数
    1. ckey: 密钥

    返回值示例
    True
    """

    skey = "xxxxxxxxxx"
    return skey == ckey


def recv_command(conn):  # ok
    """
    处理 master 派发的任务，只负责转发任务与返回结果
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

    if not msg:
        pass

    mission = json.loads(msg)
    commands = mission["mission"]  # 具体指令

    if commands == "cmd2slave":
        conn.sendall(st.cmd2slave(mission["commands"]))

    elif commands == "cmd2docker":
        conn.sendall(st.cmd2docker(mission["commands"]))

    elif commands == "reload":
        dicts = {
            "code": 1,
            "msg": "",
            "result": ""
        }

        try:
            reload(st)
            dicts["code"] = 0
        except Exception, e:
            print put_color("reload module stoolbox failed\n  [-]"+str(e), "red")
            print traceback.format_exc()
            print "-"*50
            dicts["msg"] = str(e)

        conn.sendall(json.dumps(dicts))

    else:
        print put_color("aborted command: %s" % commands, "red")
        conn.sendall(json.dumps({
            "code": 1,
            "msg": "This mission is out of slave's ability...",
            "result": ""
        }))


"""
监听端口，负责建立通信

1. ip: 允许接入的 ip；默认为 0.0.0.0, 即任意 ip
2. port: 监听的端口; 可选参数; 默认为 1100
"""

ip = '0.0.0.0'
port = 1100
sk = socket.socket()
sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sk.bind((ip, port))
sk.listen(1)

print put_color('slave is online', "green")

while 1:
    try:
        conn, from_ip = sk.accept()
    except:
        print put_color('slave is offline', "red")
        break

    client_data = conn.recv(1024)
    if sign_in(client_data):
        conn.sendall('hello, my master')

        try:
            recv_command(conn)
        except Exception, e:
            print put_color("something went wrong\n  [-]"+str(e), "red")
            print traceback.format_exc()
            print "-"*50
            conn.sendall(json.dumps({
                "code": 1,
                "msg": str(e),
                "result": "",
            }))

    else:
        msg = "tell %s: silence is gold" % from_ip
        print put_color(msg, "yellow")
        conn.sendall(msg)

    conn.close()
