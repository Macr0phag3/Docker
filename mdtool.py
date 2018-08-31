# -*- coding: utf-8 -*-
from toolboxs import mtoolbox as mt
from toolboxs import ptoolbox as pt
from goto import with_goto
from pprint import pprint
import sys
import signal
import json
import random


def abort(a, b):  # ok
    if b != 0:
        show_logo()

    sys.exit(pt.put_color(
        random.choice([
            "Goodbye", "Have a nice day",
            "See you later", "Bye",
            "Farewell", "Cheerio",
        ]), "white"))


def colored_choice(num):
    num_color = [pt.put_color(str(i), "blue") for i in range(num)]
    alpha_color = [pt.put_color(i, "yellow") for i in ['b', 'q']]
    return num_color + alpha_color


def cls():  # ok
    print "\033c"


def show_logo():  # ok
    cls()
    print """
    %s\
    %s\
%s""" % (pt.put_color("""
      .-""`""-.
  __/`oOoOoOoOo`\__
  '.-=-=-=-=-=-=-.'
    `-=.=-.-=.=-'
       ^  ^  ^\
    """, "yellow"),  pt.put_color("""
hack it and docker it
""", "green"), pt.put_color("======================\n", "white"))


@with_goto
def Main_menu():  # ok
    label .main
    choice = raw_input("""
==========
{}: 基本操作
{}: 更多操作
{}: 退出
==========
输入序号> """.format(*[i for i in colored_choice(2) if "b" not in i]))

    show_logo()
    if choice == '0':
        basic_menu()

    elif choice == '1':
        pro_menu()

    elif choice == 'q':
        abort(1, 1)
    else:
        print pt.put_color("输入有误, 重新输入", "red")

    goto .main


@with_goto
def nk_menu():
    label .network
    choice = raw_input("""
==================
输入数字以继续:
{}: 检查连接
{}: 显示可用 ip
{}: 显示已用 ip
{}: 返回
{}: 退出
==================
> """.format(*colored_choice(3)))

    subnet = get_setting("bridge")["subnet"]
    show_logo()

    if choice == '1':
        mission = {
            "mission": "cmd2slave",
            "commands": {
                "command": "check_alive",
                "arg": [subnet]
            }
        }

        ips = get_setting("slave_ip")
        for ip in ips:
            result = json.loads(mt.command2slave(ip, json.dumps(mission), timeout=10))
            if result["code"]:
                print pt.put_color(ip, "red"), pt.put_color(
                    u"内网", "red"), pt.put_color(u"外网", "red")
            else:
                if result["result"]:
                    print pt.put_color(ip, "yellow"), pt.put_color(
                        u"内网", "green"), pt.put_color(u"外网", "red")
                else:
                    print pt.put_color(ip, "green"), pt.put_color(
                        u"内网", "green"), pt.put_color(u"外网", "green")

    elif choice == '2':
        result = json.loads(mt.ip_ls(subnet))
        if result["code"]:
            print pt.put_color(u"获取可用 ip 出错", "red")
            print "原因如下:\n", result["msg"]
        else:
            print pt.put_color("获取可用 ip 成功", "green")
            print "结果如下:"
            pprint(result["result"])

    elif choice == '3':
        result = json.loads(mt.ip_used(subnet))
        if result["code"]:
            print pt.put_color(u"获取已用 ip 出错", "red")
            print "原因如下:\n", result["msg"]
        else:
            print pt.put_color("获取已用 ip 成功", "green")
            print "结果如下:"
            pprint(result["result"])

    elif choice == 'b':
        return

    elif choice == 'q':
        abort(1, 1)

    else:
        print pt.put_color("输入有误, 重新输入", "red")

    goto .network


signal.signal(signal.SIGINT, abort)
signal.signal(signal.SIGTERM, abort)

show_logo()
Main_menu()
