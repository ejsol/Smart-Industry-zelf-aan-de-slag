#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) EJSol 8 jun 2019 freeware for use in Smart Industry - Zelf Aan de Slag workshop (SIZAS)
#
# standalone, very simple, no user interface,
# start from command line, control the doors and log the accurate warehouse temperature
# this version -1x- is a little different in amount of grove sensors (only one high accuracy temperature, not three)

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
        # Low = pressed
        self.__led = Factory.getOneLed("GPIO-HIGH", pin)
        self.__btn = Factory.getButton("GPIO-LOW", pin + 1)
        self.__led.light(False)
        self.__on_release = None
        self.__on_press = None
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


Grove = GroveLedButton

main_state = False
door_1_state = False
door_2_state = False


def main():

    global main_state, door_1_state, door_2_state

    main_button = GroveLedButton(5)
    door_1_button = GroveLedButton(18)
    door_2_button = GroveLedButton(16)

    main_relay = GroveRelay(22)
    door_1_relay = GroveRelay(26)
    door_2_relay = GroveRelay(24)

    sensor = Factory.getTemper("MCP9808-I2C")
    sensor.resolution(Temper.RES_1_16_CELSIUS)

    def on_press_main():
        global main_state, door_1_state, door_2_state
        if main_state:
            main_state = False
            door_1_state = False
            door_2_state = False
            main_relay.off()
            door_1_relay.off()
            door_2_relay.off()
            main_button.led_off()
            door_1_button.led_off()
            door_2_button.led_off()
        else:
            main_state = True
            main_relay.on()
            main_button.led_on()

    def on_press_1():
        global main_state, door_1_state
        if main_state:
            if door_1_state:
                door_1_state = False
                door_1_relay.off()
                door_1_button.led_off()
            else:
                if not door_2_state:
                    door_1_state = True
                    door_1_relay.on()
                    door_1_button.led_on()

    def on_press_2():
        global main_state, door_2_state
        if main_state:
            if door_2_state:
                door_2_state = False
                door_2_relay.off()
                door_2_button.led_off()
            else:
                if not door_1_state:
                    door_2_state = True
                    door_2_relay.on()
                    door_2_button.led_on()

    main_button.on_press = on_press_main
    door_1_button.on_press = on_press_1
    door_2_button.on_press = on_press_2

    while True:
        try:
            time.sleep(1)
            print('{} Celsius'.format(sensor.temperature))
        except KeyboardInterrupt:
            main_relay.off()
            door_1_relay.off()
            door_2_relay.off()
            main_button.led_off()
            door_1_button.led_off()
            door_2_button.led_off()
            print("exit")
            exit(1)


if __name__ == '__main__':
    main()
