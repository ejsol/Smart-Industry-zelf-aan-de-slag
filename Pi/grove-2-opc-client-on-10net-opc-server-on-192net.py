#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) EJSol 8 jun 2019 freeware for use in Smart Industry - Zelf Aan de Slag workshop (SIZAS)
#
# the source is for the Pi-4  with three sensors,
# in this version for the instruction Pi-11 till Pi-16 the outside temperature and air quality are not used
# as the Pi-11 Pi-16 have only digital I/O and 1 high accuracy temperature sensor
#
# for the instruction Pi you need to change in line 16 the IP number from 10.0.0.10 to 10.0.0.1x with 1<x<6
# and if Pi is behind firewall then call 10.0.0.254:54844 in case of Pi-4 (of else 54840+1x)

from opcua import Client
import time

# YOU NEED CHANGE THE PI-1x 10.0.0.1x into 192.168.0.1x and wired your Pi-1x to the router with an Ethernet cable
url ="opc.tcp://10.0.0.254:54850" # =54840 + your pi nr, e.g. Pi-11 goes to 54851   which is translated into 192.168.0.11:4840 by the firewall/router DSTNAT

client = Client(url)

client.connect()
print("Client is connected")


print("                                                             T = temperature in Celsius")
print("time                     trigger  warehouse-state outside-door  inside-door T-warehouse")


while True:
    try:
        temperature_time = client.get_node("ns=2;i=2")
        trigger = client.get_node("ns=2;i=3")
        warehouse_state = client.get_node("ns=2;i=4")
        door_outside = client.get_node("ns=2;i=5")
        door_inside = client.get_node("ns=2;i=6")
        temperature_warehouse = client.get_node("ns=2;i=7")

        print(temperature_time.get_value(), "  ", trigger.get_value(), "     ",
            int(warehouse_state.get_value()), "          ", int(door_outside.get_value()), "           ",
            int(door_inside.get_value()),"         ", temperature_warehouse.get_value())
        time.sleep(5)
    except KeyboardInterrupt:
        client.disconnect()
        exit(1)