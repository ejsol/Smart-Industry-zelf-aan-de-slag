#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Main program."""
__author__ = "Egbert-Jan Sol"
__copyright__ = "Copyright (C) Egbert-Jan Sol"
__license__ = "GPLv3"
__version__ = "0.1.1"

# standalone, start from windows environment, with full user interface to control doors and update temperature
# and control the doors with I/O too and log the accurate warehouse temperature and stop button in user interface


import time
import tkinter as tk    # conflict with Button

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


class MyGroveStandAloneApp(tk.Frame):

    def __init__(self, master=None):

        self.warehouse_state = False
        self.door_outside_state = False
        self.door_inside_state = False
        self.door_count = 0
        self.system_on_time = 0
        self.system_on = 0
        self.system_delta_time = 0
        self.door_open_time = 0
        self.door_time = 0

        self.warehouse_button = GroveLedButton(5)
        self.door_outside_button = GroveLedButton(18)
        self.door_inside_button = GroveLedButton(16)

        self.warehouse_button.on_press = self.on_press_main
        self.door_outside_button.on_press = self.on_press_door_outside
        self.door_inside_button.on_press = self.on_press_door_inside

        self.warehouse_relay = GroveRelay(22)
        self.door_outside_relay = GroveRelay(26)
        self.door_inside_relay = GroveRelay(24)

        self.sensor_w = Factory.getTemper("MCP9808-I2C")
        self.sensor_o = Factory.getTemper("NTC-ADC", 0)
        self.sensor_w.resolution(Temper.RES_1_16_CELSIUS)
        print('{} Celsius warehouse temperature'.format(self.sensor_w.temperature))
        print('{} Celsius outside temperature'.format(int(self.sensor_o.temperature)))

        self.sensor_air = GroveAirQualitySensor(4)
        print('{} Air Quality'.format(self.sensor_air.value))

        # Handle tkinter part
        super().__init__(master)
        self.master.protocol("WM_DELETE_WINDOW", self.close_app)

        self.master.wm_title("Warehouse")
        self.master.wm_resizable(width=False, height=False)
        fontlabel = ('helvetica', 15, 'bold')

        # top row names

        self.lbl_main = tk.Label(self.master, text="System", width=15, font=fontlabel)
        self.lbl_main.grid(row=0, column=0)

        self.lbl_door_outside = tk.Label(self.master, text="Outside Door", width=15, font=fontlabel)
        self.lbl_door_outside.grid(row=0, column=1)

        self.lbl_door_inside = tk.Label(self.master, text="Inside Door", width=15, font=fontlabel)
        self.lbl_door_inside.grid(row=0, column=2)

        self.lbl_info = tk.Label(self.master, text="Data", width=15, font=fontlabel)
        self.lbl_info.grid(row=0, column=3)

        # top row with switches (buttons) in on state (red, grayed in off mode)

        self.btn_warehouse_on = tk.Button(self.master, text="Turn System On", width=15)
        # only screen control after physical switch (event_warehouse_switch) is turned on, then button is also active
        self.btn_warehouse_on["command"] = self.on_press_main
        self.btn_warehouse_on.grid(row=1, column=0)

        self.btn_door_outside_open = tk.Button(self.master, text="Open Outside Door", width=15)
        self.btn_door_outside_open["command"] = self.on_press_door_outside
        self.btn_door_outside_open.grid(row=1, column=1)

        self.btn_door_inside_open = tk.Button(self.master, text="Open Inside Door", width=15)
        self.btn_door_inside_open["command"] = self.on_press_door_inside
        self.btn_door_inside_open.grid(row=1, column=2)

        self.lbl_energy = tk.Label(self.master, text="loss: 0", width=15, height=4)
        self.lbl_energy.grid(row=1, column=3)

        # Status information in middle row

        self.lbl_state_main = tk.Label(self.master, bg='light grey', text="OFF", width=15, height=4)
        self.lbl_state_main.grid(row=2, column=0)

        self.lbl_state_door_outside = tk.Label(self.master, bg='light grey', text="Closed", width=15, height=4)
        self.lbl_state_door_outside.grid(row=2, column=1)

        self.lbl_state_door_inside = tk.Label(self.master, bg='light grey', text="Closed", width=15, height=4)
        self.lbl_state_door_inside.grid(row=2, column=2)

        self.lbl_count = tk.Label(self.master, text="# door: 0", width=15)
        self.lbl_count.grid(row=2, column=3)

        # bottom row with switches (buttons) in off state (black button grayed in on)

        self.btn_warehouse_off = tk.Button(self.master, text="Turn System Off", width=15)
        self.btn_warehouse_off.config(bg='#00C1FF', fg='white')
        self.btn_warehouse_off["command"] = self.on_press_main
        self.btn_warehouse_off.grid(row=3, column=0)

        self.btn_door_outside_close = tk.Button(self.master, text="Close Outside Door", width=15)
        self.btn_door_outside_close.config(bg='#00C1FF', fg='white')
        self.btn_door_outside_close["command"] = self.on_press_door_outside
        self.btn_door_outside_close.grid(row=3, column=1)

        self.btn_door_inside_close = tk.Button(self.master, text="Close Inside Door", width=15)
        self.btn_door_inside_close.config(bg='#00C1FF', fg='white')
        self.btn_door_inside_close["command"] = self.on_press_door_inside
        self.btn_door_inside_close.grid(row=3, column=2)

        self.lbl_system_on = tk.Label(self.master, text="time on: 0", width=15)
        self.lbl_system_on.grid(row=3, column=3)

        self.btn_stop = tk.Button(self.master, text="Stop")
        self.btn_stop["command"] = self.close_app
        self.btn_stop.grid(row=4, column=3)

    def close_app(self):
        self.warehouse_relay.off()
        self.door_outside_relay.off()
        self.door_inside_relay.off()
        self.warehouse_button.led_off()
        self.door_outside_button.led_off()
        self.door_inside_button.led_off()

        self.warehouse_state = False
        self.door_outside_state = False
        self.door_inside_state = False

        print("exit")
        self.master.destroy()

    def on_press_main(self):
        if self.warehouse_state:
            self.warehouse_state = False
            self.warehouse_relay.off()
            self.warehouse_button.led_off()
            self.btn_warehouse_on.config(bg='#EAEAEA', fg='black')
            self.lbl_state_main.config(bg='light grey', text="Off")
            self.btn_warehouse_off.config(bg='#00C1FF', fg='white')

            self.door_outside_state = False
            self.door_outside_relay.off()
            self.door_outside_button.led_off()
            self.btn_door_outside_open.config(bg='#EAEAEA', fg='black')
            self.lbl_state_door_outside.config(bg='light grey', text="Closed")
            self.btn_door_outside_close.config(bg='#00C1FF', fg='white')

            self.door_inside_state = False
            self.door_inside_relay.off()
            self.door_inside_button.led_off()
            self.btn_door_inside_open.config(bg='#EAEAEA', fg='black')
            self.lbl_state_door_inside.config(bg='light grey', text="Closed")
            self.btn_door_inside_close.config(bg='#00C1FF', fg='white')

            # self.system_delta_time = time.time() - self.system_on
            # self.system_on_time = self.system_on_time + self.system_delta_time
            self.system_on_time = self.system_on_time + time.time() - self.system_on
            self.lbl_system_on.config(text="time on:" + str(int(self.system_on_time)))
            self.lbl_energy.config(text="loss: " + str(int(self.door_open_time)))
            self.lbl_count.config(text="# door: " + str(int(self.door_count)))
        else:
            self.warehouse_state = True
            self.warehouse_relay.on()
            self.warehouse_button.led_on()

            self.system_on = time.time()

            self.btn_warehouse_on.config(bg='#00CC00', fg='white')
            self.lbl_state_main.config(bg='#00CC00', text="ON")
            self.btn_warehouse_off.config(bg='white', fg='black')

    def on_press_door_outside(self):
        if self.warehouse_state:
            if self.door_outside_state:
                self.door_outside_state = False
                self.door_outside_relay.off()
                self.door_outside_button.led_off()

                self.btn_door_outside_open.config(bg='#EAEAEA', fg='black')
                self.lbl_state_door_outside.config(bg='light grey', text="Closed")
                self.btn_door_outside_close.config(bg='#00C1FF', fg='white')

                self.door_count = self.door_count + 1
                self.lbl_count.config(text="# door: " + str(int(self.door_count)))
                self.door_open_time = self.door_open_time + time.time() - self.door_time
                self.lbl_energy.config(text="loss: " + str(int(self.door_open_time)))
            else:
                if not self.door_inside_state:
                    self.door_outside_state = True
                    self.door_outside_relay.on()
                    self.door_outside_button.led_on()

                    self.btn_door_outside_open.config(bg='#FF0000', fg='white')
                    self.lbl_state_door_outside.config(bg='#FF0000', text="Open")
                    self.btn_door_outside_close.config(bg='white', fg='black')

                    self.door_time = time.time()

    def on_press_door_inside(self):
        if self.warehouse_state:
            if self.door_inside_state:
                self.door_inside_state = False
                self.door_inside_relay.off()
                self.door_inside_button.led_off()

                self.btn_door_inside_open.config(bg='#EAEAEA', fg='black')
                self.lbl_state_door_inside.config(bg='light grey', text="Closed")
                self.btn_door_inside_close.config(bg='#00C1FF', fg='white')

                self.door_count = self.door_count + 1
                self.lbl_count.config(text="# door: " + str(int(self.door_count)))
                self.door_open_time = self.door_open_time + time.time() - self.door_time
                self.lbl_energy.config(text="loss: " + str(int(self.door_open_time)))
            else:
                if not self.door_outside_state:
                    self.door_inside_state = True
                    self.door_inside_relay.on()
                    self.door_inside_button.led_on()

                    self.btn_door_inside_open.config(bg='#FF0000', fg='white')
                    self.lbl_state_door_inside.config(bg='#FF0000', text="Open")
                    self.btn_door_inside_close.config(bg='white', fg='black')

                    self.door_time = time.time()


if __name__ == '__main__':
    root = tk.Tk()
    MyGroveStandAloneApp(root).mainloop()
