#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) EJSol 12 sept 2019 freeware for use in Smart Industry - Zelf Aan de Slag workshop (SIZAS)
#
# app running control I/O for doors and collecting temperature data,
# start from command line and use from other computer opc client to read data from this opc server
#
# the source is for the Pi-4 (10.0.0.4) with three sensors,
# in this version the outside temperature and air quality are not used
# as it is meant for the instruction Pi-11 Pi-16 with only digital I/O and 1 high accuracy temperature sensor
#
# this 20a version is the asynchronous I/O python support basis version of OPC-UA asyncio 0.8.3 of Oliver Roulet

import asyncio
from datetime import datetime

from asyncua import Server
from grove.button import Button
from grove.factory import Factory
from grove.temperature import Temper
from grove.gpio import GPIO


class GroveRelay(GPIO):
    def __init__(self, pin):
        super(GroveRelay, self).__init__(pin, GPIO.OUT)

    def on(self):
        self.write(1)

    def off(self):
        self.write(0)


class GroveLedButton(object):
    def __init__(self, pin):
        # Low = pressed
        self.__led = Factory.getOneLed("GPIO-HIGH", pin)
        self.__btn = Factory.getButton("GPIO-LOW", pin + 1)
        self.__led.light(False)
        self.__on_press = None
        self.__on_release = None
        self.__btn.on_event(self, GroveLedButton.__handle_event)

    @property
    def on_press(self):
        return self.__on_press

    @on_press.setter
    def on_press(self, callback):
        if not callable(callback):
            return
        self.__on_press = callback

    def __handle_event(self, evt):

        self.__led.brightness = self.__led.MAX_BRIGHT

        if evt["code"] == Button.EV_LEVEL_CHANGED:
            if evt["pressed"]:
                if callable(self.__on_press):
                    self.__on_press()

    def led_on(self):
        self.__led.light(True)

    def led_off(self):
        self.__led.light(False)


warehouse_state = False
door_outside_state = False
door_inside_state = False


def on_press_main():
    global warehouse_state, door_outside_state, door_inside_state
    if warehouse_state:
        warehouse_state = False
        door_outside_state = False
        door_inside_state = False
        warehouse_relay.off()
        door_outside_relay.off()
        door_inside_relay.off()
        warehouse_button.led_off()
        door_outside_button.led_off()
        door_inside_button.led_off()
    else:
        warehouse_state = True
        warehouse_relay.on()
        warehouse_button.led_on()


def on_press_door_outside():
    global warehouse_state, door_outside_state, door_inside_state
    if warehouse_state:
        if door_outside_state:
            door_outside_state = False
            door_outside_relay.off()
            door_outside_button.led_off()
        else:
            if not door_inside_state:
                door_outside_state = True
                door_outside_relay.on()
                door_outside_button.led_on()


def on_press_door_inside():
    global warehouse_state, door_outside_state, door_inside_state

    if warehouse_state:
        if door_inside_state:
            door_inside_state = False
            door_inside_relay.off()
            door_inside_button.led_off()
        else:
            if not door_outside_state:
                door_inside_state = True
                door_inside_relay.on()
                door_inside_button.led_on()


warehouse_button = GroveLedButton(5)
door_outside_button = GroveLedButton(18)
door_inside_button = GroveLedButton(16)

warehouse_button.on_press = on_press_main
door_outside_button.on_press = on_press_door_outside
door_inside_button.on_press = on_press_door_inside

warehouse_relay = GroveRelay(22)
door_outside_relay = GroveRelay(26)
door_inside_relay = GroveRelay(24)

temperature_doors = Factory.getTemper("MCP9808-I2C", 0x18)
temperature_doors.resolution(Temper.RES_1_16_CELSIUS)
temperature_warehouse = Factory.getTemper("MCP9808-I2C", 0x19)
temperature_warehouse.resolution(Temper.RES_1_16_CELSIUS)


async def main():
    print('starting OPC server ')
    opc_server = Server()
    await opc_server.init()
    opc_url = "opc.tcp://0.0.0.0:4840"
    opc_server.set_endpoint(opc_url)

    print('starting OPC server ..')
    opc_name = "Grove-opcua-server"
    addspace = await opc_server.register_namespace(opc_name)
    print('starting OPC server ...')

    opc_node = opc_server.get_objects_node()
    param = await opc_node.add_object(addspace, "Parameters")

    opc_time = await param.add_variable(addspace, "Time", 0)
    opc_warehouse_state = await param.add_variable(addspace, "Warehouse state", 0)
    opc_door_outside = await param.add_variable(addspace, "Outside door", 0)
    opc_door_inside = await param.add_variable(addspace, "Inside door", 0)
    opc_temperature_d = await param.add_variable(addspace, "Temperature doorlock", 0.0)
    opc_temperature_w = await param.add_variable(addspace, "Temperature warehouse", 0.0)

    await opc_time.set_read_only()
    await opc_warehouse_state.set_read_only()
    await opc_door_outside.set_read_only()
    await opc_door_inside.set_read_only()
    await opc_temperature_d.set_read_only()
    await opc_temperature_w.set_read_only()

    print('starting OPC server .....')
    print("OPC UA Server started at {}".format(opc_url))
    print("time      Doors Warehouse (Celsius)")

    # is voor terminal-mode, niet voor windows mode
    async with opc_server:

        while True:
            try:
                await asyncio.sleep(2)
                time_stamp = datetime.now()
                await opc_time.set_value(time_stamp)
                await opc_temperature_d.set_value(temperature_doors.temperature)
                await opc_temperature_w.set_value(temperature_warehouse.temperature)
                print('{} {:.1f} {:.1f}'.format(time_stamp.strftime("%X"),
                                                temperature_doors.temperature,
                                                temperature_warehouse.temperature))
                await opc_warehouse_state.set_value(warehouse_state)
                await opc_door_outside.set_value(door_outside_state)
                await opc_door_inside.set_value(door_inside_state)
            except KeyboardInterrupt:
                warehouse_relay.off()
                door_outside_relay.off()
                door_inside_relay.off()
                warehouse_button.led_off()
                door_outside_button.led_off()
                door_inside_button.led_off()
                await opc_server.stop()
                print("exit")
                exit(1)


if __name__ == '__main__':
    asyncio.run(main())
