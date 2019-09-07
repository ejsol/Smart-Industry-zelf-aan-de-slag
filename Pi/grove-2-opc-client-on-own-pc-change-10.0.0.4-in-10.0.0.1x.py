#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) EJSol 8 jun 2019 freeware for use in Smart Industry - Zelf Aan de Slag workshop (SIZAS)
#
# the source is for the Pi-4 (10.0.0.4) with three sensors,
# in this version for the instruction Pi-11 till Pi-16 the outside temperature and air quality are not used
# as the Pi-11 Pi-16 have only digital I/O and 1 high accuracy temperature sensor
#
# for the instruction Pi you need to change in line 15 the IP number from 10.0.0.4 to 10.0.0.1x with 1<x<6

from opcua import Client
import time

url = "opc.tcp://10.0.0.4:4840"

client = Client(url)

client.connect()
print("Client is connected")


print("                                 T = temperature in Celsius")
print("time                     trigger  warehouse-state outside-door  inside-door T-warehouse ")


while True:
    try:
        temperature_time = client.get_node("ns=2;i=2")
        trigger = client.get_node("ns=2;i=3")
        warehouse_state = client.get_node("ns=2;i=4")
        door_outside = client.get_node("ns=2;i=5")
        door_inside = client.get_node("ns=2;i=6")
        temperature_warehouse = client.get_node("ns=2;i=7")

        print(temperature_time.get_value(), "  ", trigger.get_value(), "  ",
            warehouse_state.get_value(), "          ", door_outside.get_value(), "         ",
            door_inside.get_value(),"      ", temperature_warehouse.get_value())
        time.sleep(5)
    except KeyboardInterrupt:
        client.disconnect()
        exit(1)