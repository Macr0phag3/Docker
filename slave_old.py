# -*- coding:utf-8 -*-
import socket
import stoolbox
import json


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
    """

    msg = conn.recv(1024)

    if not msg:
        pass

    mission = json.loads(msg)
    command = mission["command"]  # 具体指令

    if command == "check_alive":
        conn.sendall(stoolbox.check_alive())

    elif command == "run":
        conn.sendall(stoolbox.run(*mission["arg"]))

    elif command == "others_cmd":
        conn.sendall(stoolbox.others_cmd(*mission["arg"]))

    elif command == "containers_ls":
        conn.sendall(stoolbox.containers_ls())

    elif command == "load_ls":
        conn.sendall(stoolbox.load_ls())

    elif command == "images_ls":
        conn.sendall(stoolbox.images_ls())

    elif command == "ip_used_ls":
        conn.sendall(stoolbox.ip_used_ls(*mission["arg"]))

    else:
        print put_color("aborted command: %s" % command, "red")
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
        recv_command(conn)
    else:
        msg = "tell %s: silence is gold" % from_ip
        print put_color(msg, "yellow")
        conn.sendall(msg)

    conn.close()