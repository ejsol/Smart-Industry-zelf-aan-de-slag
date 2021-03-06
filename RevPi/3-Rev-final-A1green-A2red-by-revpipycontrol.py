#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) EJSol 1 jul 2019 freeware for use in Smart Industry - Zelf Aan de Slag workshop (SIZAS)
#
# demo with more functionality to be started with e.g. Revpipycontrol from remote
# or from RevPi itself using: python3 Rev-demo-... or after making it executable (chmod +x Rev*) using: ./Rev-demo-..
# check after killing it with: ps -ae is process has stopped, else get the process id (pid) and: sudo kill -HUP pid
#
# main_switch, switch_1 and switch_2, main_relay, etc input/output are all defined in Kunbus piCtory
#
# piCtory Setup: RevPICore | DIO
#
# I_1 main_switch
# I_3 switch_1
# I_5 switch_2
#
# O_1 main_relay
# O_3 relay_1
# O_5 relay_2
#
# A1green LED indicates running program, A2red indicated system is on (main_switch on, main_state = True)
#

import revpimodio2


class MyRevPiApp:

    def __init__(self):
        """Init MyRevPiApp class."""

        # Instantiate RevPiModIO
        self.rpi = revpimodio2.RevPiModIO(autorefresh=True)

        # Handle SIGINT / SIGTERM to exit program cleanly
        self.rpi.handlesignalend(self.cleanup_revpi)

        # Register event to toggle output O_1 with input I_1
        self.rpi.io.main_switch.reg_event(self.event_main_on, edge=revpimodio2.RISING)
        self.rpi.io.main_switch.reg_event(self.event_main_off, edge=revpimodio2.FALLING)

        # Register event to toggle output O_3 with input I_3
        self.rpi.io.switch_1.reg_event(self.event_switch_1_on, edge=revpimodio2.RISING)
        self.rpi.io.switch_1.reg_event(self.event_switch_1_off, edge=revpimodio2.FALLING)

        # Register event to toggle output O_5 with input I_5
        self.rpi.io.switch_2.reg_event(self.event_switch_2_on, edge=revpimodio2.RISING)
        self.rpi.io.switch_2.reg_event(self.event_switch_2_off, edge=revpimodio2.FALLING)

        self.rpi.core.a1green.value = True      # program is loaded and active
        self.rpi.core.a1red.value = False
        self.rpi.core.a2green.value = False
        self.rpi.core.a2red.value = False

        self.rpi.io.main_relay.value = False   # O 1 (output 1) right side connector on DIO is odd input/output nr
        self.rpi.io.relay_1.value = False      # O 3
        self.rpi.io.relay_2.value = False      # O 5

        self.main_state = False
        self.state_1_on = False
        self.state_2_on = False

    def cleanup_revpi(self):
        """Cleanup function to leave the RevPi in a defined state."""
        # Switch off LED and outputs before exit program
        self.rpi.core.a1green.value = False
        self.rpi.core.a1red.value = False
        self.rpi.io.main_relay.value = False
        self.rpi.io.relay_1.value = False
        self.rpi.io.relay_2.value = False
        self.rpi = revpimodio2.RevPiModIO(autorefresh=False)

    def event_main_on(self, ioname, iovalue):
        """Called if main_switch goes to True."""
        # Switch on/off output O_1
        self.rpi.core.a2red.value = True
        self.rpi.io.main_relay.value = True
        self.main_state = True

    def event_main_off(self, ioname, iovalue):
        """Called if main_switch goes to false."""
        # Switch on/off output O_1
        self.rpi.io.main_relay.value = False
        self.rpi.io.relay_1.value = False
        self.rpi.io.relay_2.value = False
        self.rpi.core.a2red.value = False
        self.main_state = False

    def event_switch_1_on(self, ioname, iovalue):
        """Called if I_3 goes to True."""
        if self.main_state and not self.state_2_on:
            self.rpi.io.relay_1.value = True
            self.state_1_on = True

    def event_switch_1_off(self, ioname, iovalue):
        """Called if I_3 goes to false."""
        if self.main_state:
            self.rpi.io.relay_1.value = False
            self.state_1_on = False

    def event_switch_2_on(self, ioname, iovalue):
        """Called if I_5 goes to True."""
        if self.main_state and not self.state_1_on:
            self.rpi.io.relay_2.value = True
            self.state_2_on = True

    def event_switch_2_off(self, ioname, iovalue):
        """Called if I_5 goes to False."""
        if self.main_state:
            self.rpi.io.relay_2.value = False
            self.state_2_on = False

    def start(self):
        """Start event system and own cyclic loop."""

        # Start event system without blocking here
        self.rpi.mainloop(blocking=False)

        # My own loop to do some work next to the event system. We will stay
        # here till self.rpi.exitsignal.wait returns True after SIGINT/SIGTERM
        while not self.rpi.exitsignal.wait(1):

            # Switch on / off green part of LED A1 to signal to user that PLC runs
            self.rpi.core.a1green.value = not self.rpi.core.a1green.value

            if self.main_state:  # if main_state is on flip-flop between a1 green and a2 red
                if self.rpi.core.a1green.value:
                    self.rpi.core.a2red.value = True
                else:
                    self.rpi.core.a2red.value = False


if __name__ == "__main__":
    root = MyRevPiApp()
    root.start()
