#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) EJSol 8 jun 2019 freeware for use in Smart Industry - Zelf Aan de Slag workshop (SIZAS)
#
# app running control I/O for doors and collecting temperature data,
# start from command line and use from other computer opc client to read data from this opc server

import time
from datetime import datetime
# import tkinter as tk
from opcua import Server
from grove.button import Button
from grove.factory import Factory
from grove.temperature import Temper
from grove.adc import ADC
from grove.gpio import GPIO


class GroveRelay(GPIO):
    def __init__(self, pin):
        super(GroveRelay, self).__init__(pin, GPIO.OUT)

    def on(self):
        self.write(1)

    def off(self):
        self.write(0)


class GroveAirQualitySensor:
    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()

    @property
    def value(self):
        return self.adc.read(self.channel)


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


class MyGroveOpcTerminalApp:

    def __init__(self):

        self.warehouse_state = False
        self.door_outside_state = False
        self.door_inside_state = False

        self.warehouse_button = GroveLedButton(5)
        self.door_outside_button = GroveLedButton(18)
        self.door_inside_button = GroveLedButton(16)

        self.warehouse_button.on_press = self.on_press_main
        self.door_outside_button.on_press = self.on_press_door_outside
        self.door_inside_button.on_press = self.on_press_door_inside

        self.warehouse_relay = GroveRelay(22)
        self.door_outside_relay = GroveRelay(26)
        self.door_inside_relay = GroveRelay(24)

        self.time_stamp = datetime.now()
        self.temperature_doors = Factory.getTemper("MCP9808-I2C", 0x18)
        self.temperature_doors.resolution(Temper.RES_1_16_CELSIUS)
        self.temperature_warehouse = Factory.getTemper("MCP9808-I2C", 0x19)
        self.temperature_warehouse.resolution(Temper.RES_1_16_CELSIUS)
        self.temperature_outdoor = Factory.getTemper("NTC-ADC", 0x00, 2)
        # 2 implies on the grove base hat board port A2, top row, last port)
        self.warehouse_air_quality = GroveAirQualitySensor(6)
        # 6 implies on the grove base hat board port A6, middle row, last port
        # print('{} Celsius warehouse temperature'.format(self.temperature_warehouse.temperature))
        # print('{} Celsius outside temperature'.format(int(self.temperature_outdoor.temperature)))
        # print('{} Air Quality (carbon monoxide & other gasses'.format(self.warehouse_air_quality.value))

        print('starting OPC server ')
        self.opc_server = Server(shelffile="/home/pi/grove-opc-server")
        #shelffile is trick with freeopcua to speedup loading of xml object base
        self.opc_url = "opc.tcp://0.0.0.0:4840"
        self.opc_server.set_endpoint(self.opc_url)

        print('starting OPC server ..')
        self.opc_name = "Grove-opcua-server"
        self.addspace = self.opc_server.register_namespace(self.opc_name)
        print('starting OPC server ...')

        self.opc_node = self.opc_server.get_objects_node()
        self.param = self.opc_node.add_object(self.addspace, "Parameters")

        self.opc_time = self.param.add_variable(self.addspace, "Time", 0)
        self.opc_temperature_w = self.param.add_variable(self.addspace, "Temperature warehouse", 0.0)
        self.opc_temperature_d = self.param.add_variable(self.addspace, "Temperature door-lock", 0.0)
        self.opc_temperature_o = self.param.add_variable(self.addspace, "Temperature outdoor", 0.0)
        self.opc_warehouse_air = self.param.add_variable(self.addspace, "Warehouse air", 0.0)
        self.opc_trigger = self.param.add_variable(self.addspace, "Trigger", 0)
        self.opc_warehouse_state = self.param.add_variable(self.addspace, "Warehouse state", 0)
        self.opc_door_outside = self.param.add_variable(self.addspace, "Outside door", 0)
        self.opc_door_inside = self.param.add_variable(self.addspace, "Inside door", 0)

        self.opc_time.set_read_only()
        self.opc_temperature_w.set_read_only()
        self.opc_temperature_d.set_read_only()
        self.opc_temperature_o.set_read_only()
        self.opc_warehouse_air.set_read_only()
        self.opc_trigger.set_read_only()
        self.opc_warehouse_state.set_read_only()
        self.opc_door_outside.set_read_only()
        self.opc_door_inside.set_read_only()

        print('starting OPC server .....')
        self.opc_server.start()
        print("OPC UA Server started at {}".format(self.opc_url))
        print()
        print("                                                   T = temperature Celsius")
        print("time     trigger  warehouse outside-door  inside-door Q-air  T-outdoor  T-doors T-warehouse")

    def closeapp(self):
        self.warehouse_relay.off()
        self.door_outside_relay.off()
        self.door_inside_relay.off()
        self.warehouse_button.led_off()
        self.door_outside_button.led_off()
        self.door_inside_button.led_off()
        self.opc_server.stop()
        print("exit")
        # self.master.destroy()
        exit(1)

    def update_opc(self, trigger):
        self.time_stamp = datetime.now()
        self.opc_time.set_value(self.time_stamp)
        self.opc_temperature_w.set_value(self.temperature_warehouse.temperature)
        self.opc_temperature_d.set_value(self.temperature_doors.temperature)
        self.opc_temperature_o.set_value(int(self.temperature_outdoor.temperature))
        self.opc_warehouse_air.set_value(self.warehouse_air_quality.value)
        self.opc_trigger.set_value(trigger)
        self.opc_warehouse_state.set_value(self.warehouse_state)
        self.opc_door_outside.set_value(self.door_outside_state)
        self.opc_door_inside.set_value(self.door_inside_state)
        print('{} '.format(self.time_stamp.strftime("%X")),
              trigger, "       ",
              int(self.warehouse_state), "          ",
              int(self.door_outside_state), "         ",
              int(self.door_inside_state), "        ",
              self.warehouse_air_quality.value, "  ",
              int(self.temperature_outdoor.temperature), "      ",
              self.temperature_doors.temperature, "  ",
              self.temperature_warehouse.temperature)

    def on_press_main(self):
        if self.warehouse_state:
            self.warehouse_state = False
            self.door_outside_state = False
            self.door_inside_state = False
            self.warehouse_relay.off()
            self.door_outside_relay.off()
            self.door_inside_relay.off()
            self.warehouse_button.led_off()
            self.door_outside_button.led_off()
            self.door_inside_button.led_off()
        else:
            self.warehouse_state = True
            self.warehouse_relay.on()
            self.warehouse_button.led_on()
        self.update_opc(1)

    def on_press_door_outside(self):
        if self.warehouse_state:
            if self.door_outside_state:
                self.door_outside_state = False
                self.door_outside_relay.off()
                self.door_outside_button.led_off()
            else:
                if not self.door_inside_state:
                    self.door_outside_state = True
                    self.door_outside_relay.on()
                    self.door_outside_button.led_on()
        self.update_opc(2)

    def on_press_door_inside(self):
        if self.warehouse_state:
            if self.door_inside_state:
                self.door_inside_state = False
                self.door_inside_relay.off()
                self.door_inside_button.led_off()
            else:
                if not self.door_outside_state:
                    self.door_inside_state = True
                    self.door_inside_relay.on()
                    self.door_inside_button.led_on()
        self.update_opc(3)

    # start function is for terminal-mode, not usable in windows mode, there we use the widget.after method
    def start(self):
        """Start event system and own cyclic loop."""

        while True:
            try:
                # dirty temp (client changes every 5 sec opc_warehouse_state)
                if self.opc_warehouse_state.get_value():
                    self.warehouse_button.led_on()
                else:
                    self.warehouse_button.led_off()
                time.sleep(5)
                self.update_opc(0)
            except KeyboardInterrupt:
                self.closeapp()


if __name__ == '__main__':
    myapp = MyGroveOpcTerminalApp()
    myapp.start()
