# -*- coding: utf-8 -*-
from api import env
import stoolbox
from goto import with_goto
from pprint import pprint
import sys
import signal
import socket
import json
import re


def abort(a, b):
    sys.exit("\nBye~")


@with_goto
def Main_menu():
    label .main
    choice = raw_input(
        """
=============
输入数字以继续:
1. 桥接
2. 取消桥接
3: 显示负载
4: 显示已用 ip
0. 退出
=============
输入数字以继续: """
    )
    stoolbox.cls()
    setting = mtoolbox.load_setting("bridge")
    subnet = setting["subnet"]
    master_ip = setting["master_ip"]
    iface = setting["iface"]
    gateway = setting["gateway"]

    if choice == '1':
        result = json.loads(stoolbox.nk_bridge(subnet, master_ip, iface, gateway))
        if result["code"]:
            print stoolbox.put_color("桥接失败", "red")
            print result["msg"]
        else:
            print stoolbox.put_color("桥接成功", "green")

    elif choice == '2':
        result = json.loads(stoolbox.nk_unbridge())
        if result["code"]:
            print stoolbox.put_color("取消桥接失败", "red")
            print result["msg"]
        else:
            print stoolbox.put_color("取消桥接成功", "green")

    elif choice == '3':
        pprint(stoolbox.load_ls())

    elif choice == '4':
        pprint(stoolbox.ip_used_ls(subnet))

    elif choice == '0':
        sys.exit("Bye~")

    else:
        print stoolbox.put_color("输入有误, 重新输入", "red")

    goto .main


signal.signal(signal.SIGINT, abort)
signal.signal(signal.SIGTERM, abort)
Main_menu()
