#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) EJSol 8 jun 2019 freeware for use in Smart Industry - Zelf Aan de Slag workshop (SIZAS)

from opcua import Client
import time

url = "opc.tcp://10.0.1.253:4843"

client = Client(url)

client.connect()
print("Client is connected ")
print(" ")
print(" log file with data for database storage")

print("                               ")
print("time stamp                trigger  system on out-door  in-door  open% out/in door %")


while True:
    try:
        time_stamp = client.get_node("ns=2;i=2")
        trigger = client.get_node("ns=2;i=3")
        warehouse_state = client.get_node("ns=2;i=4")
        door_outside = client.get_node("ns=2;i=5")
        door_inside = client.get_node("ns=2;i=6")
        open_percentage = client.get_node("ns=2;i=7")
        door_share_percentage = client.get_node("ns=2;i=8")
        print(time_stamp.get_value(), "  ", trigger.get_value(), "  ", warehouse_state.get_value(), "     ",
            door_outside.get_value(), "     ", door_inside.get_value(), " ",
            int(open_percentage.get_value()), "  ", int(door_share_percentage.get_value()))
        time.sleep(5)
    except KeyboardInterrupt:
        client.disconnect()
        exit(1)
