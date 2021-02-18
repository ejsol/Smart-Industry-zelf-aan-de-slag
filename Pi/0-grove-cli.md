This is the start of the program where the Python libraries are loaded


```python
#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) EJSol 12 sept 2019 freeware for use in Smart Industry - Zelf Aan de Slag workshop (SIZAS)
#
# standalone, very simple, no user interface,
# start from command line, control the doors and log the accurate warehouse temperature
# this version -1x- is a little different in amount of grove sensors (only one high accuracy temperature, not three)

import time
from datetime import datetime
from grove.button import Button
from grove.factory import Factory
from grove.temperature import Temper
from grove.gpio import GPIO
```

Controlling the relays is simple, you need to figure out the address of a pin/connecter and then you can set the bit value and with it the digital output on/off. 

Lateron the relay for door 1 (symbolic address door\_1_\relay) is address 26, so the call becomes GroveRelay(26)
and the object door\_1\_relay (the self in the class definition) is set on/off by the statement: door\_1\_relay.on of .off


```python
class GroveRelay(GPIO):
    def __init__(self, pin):
        super(GroveRelay, self).__init__(pin, GPIO.OUT)

    def on(self):
        self.write(1)

    def off(self):
        self.write(0)
```

Below things get more complicated as a LedButton does two things. An output (the Led) is still simple, similar to the relay above, see the last lines of the class definition. The input, the Button, is complex. It requires an (interupt) event and in reallife one has to deal with jitter of whether the button around a few millisecond is pressed or not. But we focus here on explaining the event handling.  

An event has an event handler and the definition of an event. Below we first define the event: on_press and then the event handler. In our case the event handler (turns on the LED at max briteness and) determines whether the button status has changed from level. This is the most simple way to describe it


```python
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
```

Ok, global variables are not advised, read normally considered not done, but for this small program no problem and straighforward.


```python
Grove = GroveLedButton

main_state = False
door_1_state = False
door_2_state = False
```

Below we assign the buttons and relay to I/O addresses. If the connectors at the Grove Pi hat are changed, then you need to figure out with button/relay is related to which value and adapt the code below accordingly.

Then the two I2C temperature sensors are coupled to the I2C addresses. This is not standard available in today's Grove library. If you experiment yourself use one analogue sensor (not so accurate) and one high accuracy I2C sensor. In the SIZAS documentation it is written what is needed to change the grove library and to solder the second I2C sensor to another address. 

If everything has gone according to plan, then on the console you will receive a first printout statement  


```python
def main():

    global main_state, door_1_state, door_2_state

    main_button = GroveLedButton(5)
    door_1_button = GroveLedButton(18)
    door_2_button = GroveLedButton(16)
    main_relay = GroveRelay(22)
    door_1_relay = GroveRelay(26)
    door_2_relay = GroveRelay(24)

    sensor_d = Factory.getTemper("MCP9808-I2C", 0x18)
    sensor_d.resolution(Temper.RES_1_16_CELSIUS)
    sensor_w = Factory.getTemper("MCP9808-I2C", 0x19)
    sensor_w.resolution(Temper.RES_1_16_CELSIUS)

    print('Time Temp.: door & warehouse (C)')
```

Now comes the logic of the I/O (PLC type) input (button) output (relay) part where only if the system is turned on, the switches 1 and 2 can control the door relays of the doors 1 and 2 with the condition that if door 1 is open, door 2 must be closed and vice versa. 


```python
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
```

Now, once you press a button, then the corresponding function is called, i.e. if the event that e.g. the main\_button is pressed the event handler is trigger and the function on\_press\_main is executed. This is a little wierd to grasp this Python interupt event mechanism. Where as below in the while loop the system sleeps, any interupt event of the three interupt events can occure and if one does, the function is executed. Nothing more.  


```python
    main_button.on_press = on_press_main
    door_1_button.on_press = on_press_1
    door_2_button.on_press = on_press_2
```

Now everthing is set ready and we go 1 second to sleep and then write an update of the temperature, sleep again, write again, etc until the user interupts the program by a keyboard interupt by typing e.g. Ctrl-C. In parallel during a sleep the button interupts can occure. 


```python
    while True:
        try:
            time.sleep(1)
            print('{}   {:.1f}   {:.1f}'.format(datetime.now().strftime("%X"), sensor_d.temperature, sensor_w.temperature))
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
```
