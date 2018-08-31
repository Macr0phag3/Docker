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
def basic_menu():
    label .network
    choice = raw_input("""
==================
输入数字以继续:
{}: 分配容器
{}: 回收容器
{}: 查看镜像
{}: 查看容器
{}: 检查连接
{}: 返回
{}: 退出
==================
> """.format(*colored_choice(5)))

    show_logo()

    if choice == "1":
        result = json.loads(mt.ip_assign(subnet))
        if result["code"]:
            print pt.put_color(u"分配 ip 失败", "red")
            print u"原因如下:\n", result["msg"]
            goto .docker

        container_ip = result["result"]
        result = json.loads(mt.check_load())
        if result["code"]:
            print pt.put_color(u"负载查询失败", "red")
            print u"原因如下:\n", result["msg"]
            goto .docker

        min_load = 100
        for i in result["result"]:
            for j in i:
                value = i[j]["cpu"]*0.2 + i[j]["mem"]*0.8
                if value < min_load:
                    min_load = value
                    ip = j

        image_list = json.loads(mt.command2slave(ip, json.dumps({
            "mission": "cmd2docker",
            "commands": {
                "command": "images_ls",
                "arg": []
            }})))

        if image_list["code"]:
            print pt.put_color(u"获取虚拟机: %s 的所有镜像失败" % ip, "red")
            print u"原因如下:\n", image_list["msg"]
            goto .docker

        print u"选择镜像"
        label .choice_image
        print "============="
        for i, image in enumerate(image_list["result"]):
            print "%s: %s" % (pt.put_color(str(i), "blue"), image)
        print "============="

        choice_image = raw_input("> ")
        if choice_image == "":
            show_logo()
            print pt.put_color(u"操作已取消", "yellow")
            goto .docker

        if choice_image not in [str(c) for c in range(i+1)]:
            show_logo()
            print pt.put_color("输入有误, 重新输入", "red")
            goto .choice_image

        image_name = image_list["result"][int(choice_image)]
        result = json.loads(
            mt.command2slave(
                ip, json.dumps({
                    "mission": "cmd2docker",
                    "commands": {
                        "command": "run",
                        "arg": [image_name, container_ip]
                    }})))

        if result["code"]:
            print pt.put_color("启动容器失败", "red")
            print "原因如下:\n", result["msg"]
            goto .docker

        print pt.put_color(u"[+]启动容器 %s 成功" % image_name, "green")
        print u"  [-]位于虚拟机 %s 中" % pt.put_color(ip, "white")
        print u"  [-]容器分配的 ip 为:", pt.put_color(result["result"]["ip"], "white")
        print u"  [-]ID 为", pt.put_color(result["result"]["id"], "white")

    elif choice == '4':
        mission = {
            "mission": "cmd2slave",
            "commands": {
                "command": "check_alive",
                "arg": [subnet]
            }
        }

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

    elif choice == 'b':
        return

    elif choice == 'q':
        abort(1, 1)

    else:
        print pt.put_color("输入有误, 重新输入", "red")

    goto .network


signal.signal(signal.SIGINT, abort)
signal.signal(signal.SIGTERM, abort)

ips = mt.setting["slave_ip"]
subnet = mt.setting["bridge"]["subnet"]

show_logo()
Main_menu()
