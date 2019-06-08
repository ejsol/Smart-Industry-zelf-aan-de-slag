#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) EJSol 8 jun 2019 minimal text demo based on Rev-local-switch-pyload-v1 of 3 jan
# main_switch, switch_1 and switch_2, main_relay, etc input/output are all defined in Kunbus piCtory

import revpimodio2


class MyRevPiApp:

    def __init__(self):
        """Init MyRevPiApp class."""

        # Instantiate RevPiModIO
        self.rpi = revpimodio2.RevPiModIO(autorefresh=True)

        # Handle SIGINT / SIGTERM to exit program cleanly
        self.rpi.handlesignalend(self.cleanup_revpi)

        # Register events for main_switch
        self.rpi.io.main_switch.reg_event(self.event_main_on, edge=revpimodio2.RISING)
        self.rpi.io.main_switch.reg_event(self.event_main_off, edge=revpimodio2.FALLING)

        # Register events for switch_1
        self.rpi.io.switch_1.reg_event(self.event_switch_1_on, edge=revpimodio2.RISING)
        self.rpi.io.switch_1.reg_event(self.event_switch_1_off, edge=revpimodio2.FALLING)

        # Register events for switch_2
        self.rpi.io.switch_2.reg_event(self.event_switch_2_on, edge=revpimodio2.RISING)
        self.rpi.io.switch_2.reg_event(self.event_switch_2_off, edge=revpimodio2.FALLING)

        # initialize output to False = 0 = off = no-lights
        self.rpi.io.main_relay.value = False
        self.rpi.io.relay_1.value = False
        self.rpi.io.relay_2.value = False

        # initialize states
        self.main_state = False
        self.state_1_on = False
        self.state_2_on = False

    def cleanup_revpi(self):
        """Cleanup function to leave the RevPi in a defined state."""
        # Switch off LED and outputs before exit program
        self.rpi.io.main_relay.value = False
        self.rpi.io.relay_1.value = False
        self.rpi.io.relay_2.value = False
        self.rpi = revpimodio2.RevPiModIO(autorefresh=False)

    def event_main_on(self, ioname, iovalue):
        self.rpi.io.main_relay.value = True
        self.main_state = True

    def event_main_off(self, ioname, iovalue):
        self.rpi.io.main_relay.value = False
        self.rpi.io.relay_1.value = False
        self.rpi.io.relay_2.value = False
        self.main_state = False

    def event_switch_1_on(self, ioname, iovalue):
        if self.main_state and not self.state_2_on:
            self.rpi.io.relay_1.value = True
            self.state_1_on = True

    def event_switch_1_off(self, ioname, iovalue):
        self.rpi.io.relay_1.value = False
        self.state_1_on = False

    def event_switch_2_on(self, ioname, iovalue):
        if self.main_state and not self.state_1_on:
            self.rpi.io.relay_2.value = True
            self.state_2_on = True

    def event_switch_2_off(self, ioname, iovalue):
        self.rpi.io.relay_2.value = False
        self.state_2_on = False

    def start(self):
        # Start event system without blocking here
        self.rpi.mainloop(blocking=False)

        # We stay here, switch on the LED A1 every sec, till self.rpi.exitsignal.wait returns True after SIGINT/SIGTERM
        while not self.rpi.exitsignal.wait(1):
            self.rpi.core.a1green.value = not self.rpi.core.a1green.value


if __name__ == "__main__":
    root = MyRevPiApp()
    root.start()
