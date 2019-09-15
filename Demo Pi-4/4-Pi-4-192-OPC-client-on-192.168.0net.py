#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) EJSol 8 jun 2019 freeware for use in Smart Industry - Zelf Aan de Slag workshop (SIZAS)

from opcua import Client
import time

url = "opc.tcp://192.168.0.4:4840"

client = Client(url)

client.connect()
print("Client is connected")
print("                                                                            T = temperature Celsius")
print("time           trigger  warehouse outside-door  inside-door Q-air  T-outdoor  T-warehouse")

while True:
    try:
        temperature_warehouse = client.get_node("ns=2;i=3")
        temperature_time = client.get_node("ns=2;i=2")
        temperature_outdoor = client.get_node("ns=2;i=4")
        warehouse_air = client.get_node("ns=2;i=5")
        trigger = client.get_node("ns=2;i=6")
        warehouse_state = client.get_node("ns=2;i=7")
        door_outside = client.get_node("ns=2;i=8")
        door_inside = client.get_node("ns=2;i=9")
        print('{} '.format(temperature_time.get_value().strftime("%X")), "  ", trigger.get_value(), "  ",
              int(warehouse_state.get_value()), "          ", int(door_outside.get_value()), "         ",
            int(door_inside.get_value()), "        ", warehouse_air.get_value(), "  ",
            temperature_outdoor.get_value(), "      ", temperature_warehouse.get_value())

        time.sleep(5)
    except KeyboardInterrupt:
        client.disconnect()
        exit(1)