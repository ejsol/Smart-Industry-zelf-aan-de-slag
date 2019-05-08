#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Main program."""
__author__ = "Egbert-Jan Sol"
__copyright__ = "Copyright (C) Egbert-Jan Sol"
__license__ = "GPLv3"
__version__ = "v2"

# standalone, very simple, no user interface,
# using Seeed Grove Base Hat for Raspberry Pi
# 1 x analogue input on I2C connectors using Grove I2C High accuracy temperature sensors
# 1 or 3 digital input (with LED output) on D5, (D6, D16) using Grove RYB LED button
# 1 or 3 digital output on D22, D24, D26 using Grove Relay (simple version)
# see assigns in of I/O to code name in code of main loop
# 1s = 1 switch very simple sequence, 3s = 3 switches
# start from command line, control the doors and log the accurate warehouse temperature


import time
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
        # High = light on
        self.led = Factory.getOneLed("GPIO-HIGH", pin)
        # Low = pressed
        self.__btn = Factory.getButton("GPIO-LOW", pin + 1)
        self.__on_event = None
        self.__btn.on_event(self, GroveLedButton.__handle_event)

    @property
    def on_event(self):
        return self.__on_event

    @on_event.setter
    def on_event(self, callback):
        if not callable(callback):
            return
        self.__on_event = callback

    def __handle_event(self, evt):
        # print("event index:{} event:{} pressed:{}".format(evt['index'], evt['code'], evt['presesed']))
        if callable(self.__on_event):
            self.__on_event(evt['index'], evt['code'], evt['time'])
            return

        self.led.brightness = self.led.MAX_BRIGHT
        event = evt['code']
        if event & Button.EV_SINGLE_CLICK:
            self.led.light(True)
            print("turn on  LED")
        elif event & Button.EV_DOUBLE_CLICK:
            self.led.blink()
            print("blink    LED")
        elif event & Button.EV_LONG_PRESS:
            self.led.light(False)
            print("turn off LED")


main_state = False
door_1_state = False
door_2_state = False


def main():
    global main_state, door_1_state, door_2_state

    main_button = GroveLedButton(5)
    door_1_button = GroveLedButton(18)
    door_2_button = GroveLedButton(16)

    main_relay = GroveRelay(22)
#    door_1_relay = GroveRelay(26)
#    door_2_relay = GroveRelay(24)

    sensor_1 = Factory.getTemper("MCP9808-I2C")
    sensor_1.resolution(Temper.RES_1_16_CELSIUS)

    def on_press(index, event, tm):
        global main_state, door_1_state, door_2_state
        if main_state:
            main_state = False
            door_1_state = False
            door_2_state = False
            main_relay.off()
#           door_1_relay.off()
#           door_2_relay.off()
            main_button.led.light(False)
            door_1_button.led.light(False)
            door_2_button.led.light(False)
        else:
            main_state = True
            main_relay.on()
            main_button.led.light(True)

    def on_press_1(index, event, tm):
        global main_state, door_1_state
        if main_state:
            if door_1_state:
                door_1_state = False
#                door_1_relay.off()
                door_1_button.led.light(False)
            else:
                if not door_2_state:
                    door_1_state = True
#                    door_1_relay.on()
                    door_1_button.led.light(True)

    def on_press_2(index, event, tm):
        global main_state, door_2_state
        if main_state:
            if door_2_state:
                door_2_state = False
#                door_2_relay.off()
                door_2_button.led.light(False)
            else:
                if not door_1_state:
                    door_2_state = True
#                    door_2_relay.on()
                    door_2_button.led.light(True)

    main_button.on_event = on_press
    door_1_button.on_event = on_press_1
    door_2_button.on_event = on_press_2

    while True:
        try:
            time.sleep(1)
            print('{} Celsius'.format(sensor_1.temperature))
        except KeyboardInterrupt:
            main_relay.off()
#            door_1_relay.off()
#            door_2_relay.off()
            main_button.led.light(False)
            door_1_button.led.light(False)
            door_2_button.led.light(False)
            print("exit")
            exit(1)


if __name__ == '__main__':
    main()
