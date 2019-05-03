#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Main program."""
__author__ = "Egbert-Jan Sol"
__copyright__ = "Copyright (C) Egbert-Jan Sol"
__license__ = "GPLv3"
__version__ = "0.1.1"

# app running control I/O for doors and collecting temperature data,
# start from command line and use from other computer opc client to read data froom this opc server

import time
import datetime
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


# class MyGroveOpcApp(tk.Frame):
class MyGroveOpcTerminalApp:

    # def __init__(self, master=None):
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

        self.temperature_warehouse = Factory.getTemper("MCP9808-I2C")
        self.temperature_warehouse.resolution(Temper.RES_1_16_CELSIUS)
        self.temperature_outdoor = Factory.getTemper("NTC-ADC", 0)
        self.warehouse_air_quality = GroveAirQualitySensor(4)
        # print('{} Celsius warehouse temperature'.format(self.temperature_warehouse.temperature))
        # print('{} Celsius outside temperature'.format(int(self.temperature_outdoor.temperature)))
        # print('{} Air Quality (carbon monoxide & other gasses'.format(self.warehouse_air_quality.value))


        print('starting OPC server ')
        self.opc_server = Server()
        self.opc_url = "opc.tcp://10.0.0.5:4840"
        self.opc_server.set_endpoint(self.opc_url)
        print('starting OPC server ..')
        self.opc_name = "Grove-opcua-server"
        self.addspace = self.opc_server.register_namespace(self.opc_name)
        print('starting OPC server ...')
        self.opc_node = self.opc_server.get_objects_node()
        self.param = self.opc_node.add_object(self.addspace, "Parameters")

        self.opc_time = self.param.add_variable(self.addspace, "Time", 0)
        self.opc_temperature_w = self.param.add_variable(self.addspace, "Temperature warehouse", 0)
        self.opc_temperature_o = self.param.add_variable(self.addspace, "Temperature outdoor", 0)
        self.opc_warehouse_air = self.param.add_variable(self.addspace, "Warehouse air", 0)
        self.opc_trigger = self.param.add_variable(self.addspace, "Trigger", 0)
        self.opc_warehouse_state = self.param.add_variable(self.addspace, "Warehouse state", 0)
        self.opc_door_outside = self.param.add_variable(self.addspace, "Outside door", 0)
        self.opc_door_inside = self.param.add_variable(self.addspace, "Inside door", 0)

        self.opc_time.set_writable()
        self.opc_temperature_w.set_writable()
        self.opc_temperature_o.set_writable()
        self.opc_warehouse_air.set_writable()
        self.opc_trigger.set_writable()
        self.opc_warehouse_state.set_writable()
        self.opc_door_outside.set_writable()
        self.opc_door_inside.set_writable()

        print('starting OPC server .....')
        self.opc_server.start()
        print("OPC UA Server started at {}".format(self.opc_url))

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
        self.opc_time.set_value(datetime.datetime.now())
        self.opc_temperature_w.set_value(self.temperature_warehouse.temperature)
        print('{} temperature warehouse'.format(self.temperature_warehouse.temperature))
        self.opc_temperature_o.set_value(int(self.temperature_outdoor.temperature))
        print('{} temperature outdoor'.format(int(self.temperature_outdoor.temperature)))
        self.opc_warehouse_air.set_value(self.warehouse_air_quality.value)
        print('{} warehouse air quality'.format(self.warehouse_air_quality.value))
        self.opc_trigger.set_value(trigger)
        self.opc_warehouse_state.set_value(self.warehouse_state)
        self.opc_door_outside.set_value(self.door_outside_state)
        self.opc_door_inside.set_value(self.door_inside_state)

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

    # start functie is voor terminal-mode, niet voor windows mode
    def start(self):
        """Start event system and own cyclic loop."""

        try:
            #dirty temp (client changes every 5 sec opc_warehouse_state
            if self.opc_warehouse_state.get_value():
                self.warehouse_button.led_on()
            else:
                self.warehouse_button.led_off()
            time.sleep(5)
            self.update_opc(0)
        except KeyboardInterrupt:
              self.closeapp()

if __name__ == '__main__':
    #    root = tk.Tk()
    #    MyGroveOpcApp(root).mainloop()
    myapp = MyGroveOpcTerminalApp()
    myapp.start()
