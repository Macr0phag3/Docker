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
    num_color = [pt.put_color(str(i+1), "blue") for i in range(num)]
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
def Main_menu():
    label .main
    choice = raw_input("""
==========
{}: 基本操作
{}: 更多操作
{}: 退出
==========
输入序号> """.format(*[i for i in colored_choice(2) if "b" not in i]))

    show_logo()
    if choice == '1':
        baby_menu()
    elif choice == '2':
        pro_menu()
    elif choice == 'q':
        abort(1, 1)
    else:
        print pt.put_color("输入有误, 重新输入", "red")

    goto .main
