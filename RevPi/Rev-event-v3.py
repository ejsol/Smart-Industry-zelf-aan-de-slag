#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) EJSol 3 jan
#
"""Combined events with mainloop() and own cyclic functions.

Let the LED A1 blink green during program is running.

piCtory Setup: RevPICore | DIO

main_switch I_1
switch_1 I_3
switch_2 I_5

main_relay O_1
relay_1 O_3
relay_2 O_5

v3 is changed to v2 where main control was just system active or not
    in V3 is main switch = off, then not remote control allowed, and if it is directly overwritten, 
                         = on, then remote control can override local control
                         (remote_controlled from v2 become remote_controlled,
                         but names for I_1 and O_1 remains main_switch & main_relay)
"""
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

        # Register event to toggle output O_1 with input I_1
        self.rpi.io.main_switch.reg_event(self.event_main_off, edge=revpimodio2.FALLING)

        # Register event to toggle output O_3 with input I_3
        self.rpi.io.switch_1.reg_event(self.event_switch_1_on, edge=revpimodio2.RISING)

        # Register event to toggle output O_3 with input I_3
        self.rpi.io.switch_1.reg_event(self.event_switch_1_off, edge=revpimodio2.FALLING)

        # Register event to toggle output O_5 with input I_5
        self.rpi.io.switch_2.reg_event(self.event_switch_2_on, edge=revpimodio2.RISING)

        # Register event to toggle output O_5 with input I_5
        self.rpi.io.switch_2.reg_event(self.event_switch_2_off, edge=revpimodio2.FALLING)

        '''
        # Register event to toggle output O_3 with input I_4 remote
        self.rpi.io.remote_1.reg_event(self.event_remote_1_on, edge=revpimodio2.RISING)

        # Register event to toggle output O_3 with input I_4
        self.rpi.io.remote_1.reg_event(self.event_remote_1_off, edge=revpimodio2.FALLING)

        # Register event to toggle output O_5 with input I_6 remote
        self.rpi.io.remote_2.reg_event(self.event_remote_2_on, edge=revpimodio2.RISING)

        # Register event to toggle output O_5 with input I_6
        self.rpi.io.remote_2.reg_event(self.event_remote_2_off, edge=revpimodio2.FALLING)
        '''
        self.rpi.core.a1green.value = True      # program is loaded and active
        self.rpi.core.a2red.value = False       # program does not start in remote control
        self.rpi.io.main_relay.value = False   # O 1 (output 1) right side connector on DIO is odd input/output nr
        self.rpi.io.relay_1.value = False      # O 3
        self.rpi.io.relay_2.value = False      # O 5
        self.remote_controlled = False
        self.state_1_on = False
        self.state_2_on = False

    def cleanup_revpi(self):
        """Cleanup function to leave the RevPi in a defined state."""

        # Switch of LED and outputs before exit program
        self.rpi.core.a1green.value = False
        self.rpi.core.a2red.value = False
        self.rpi.io.main_relay.value = False
        self.rpi.io.relay_1.value = False
        self.rpi.io.relay_2.value = False
        self.remote_controlled = False
        self.state_1_on = False
        self.state_2_on = False

    def event_main_on(self, ioname, iovalue):
        """Called if main_switch goes to True, here it means remoted_control is on."""
        # Switch on/off output O_1
        self.rpi.core.a2red.value = True
        self.rpi.io.main_relay.value = True
        self.remote_controlled = True

    def event_main_off(self, ioname, iovalue):
        """Called if main_switch goes to False, here it means not remote control."""
        # Switch on/off output O_1
        self.rpi.io.main_relay.value = False
        self.rpi.io.relay_1.value = False
        self.rpi.io.relay_2.value = False
        self.rpi.core.a2red.value = False
        self.remote_controlled = False

    def event_switch_1_on(self, ioname, iovalue):
        """Called if I_3 goes to True."""
        if not self.remote_controlled and not self.state_2_on:
            self.rpi.io.relay_1.value = True
            self.state_1_on = True

    def event_switch_1_off(self, ioname, iovalue):
        """Called if I_3 goes to False."""
        self.rpi.io.relay_1.value = False
        self.state_1_on = False

    def event_switch_2_on(self, ioname, iovalue):
        """Called if I_5 goes to True."""
        if not self.remote_controlled and not self.state_1_on:
            self.rpi.io.relay_2.value = True
            self.state_2_on = True

    def event_switch_2_off(self, ioname, iovalue):
        # remote of not, always switch off
        """Called if I_5 goes to False."""
        self.rpi.io.relay_2.value = False
        self.state_2_on = False

    '''
    # remote controlled input
    def event_remote_1_on(self, ioname, iovalue):
        """Called if I_3 goes to True."""
        if self.remote_controlled and not self.state_2_on:
            self.rpi.io.relay_1.value = True
            self.state_1_on = True

    def event_remote_1_off(self, ioname, iovalue):
        # remote of not switch off
        """Called if I_3 goes to True."""
        self.rpi.io.relay_1.value = False
        self.state_1_on = False

    def event_remote_2_on(self, ioname, iovalue):
        """Called if I_5 goes to True."""
        if self.remote_controlled and not self.state_1_on:
            self.rpi.io.relay_2.value = True
            self.state_2_on = True

    def event_remote_2_off(self, ioname, iovalue):
        # remote of not, always switch off
        """Called if I_5 goes to True."""
        self.rpi.io.relay_2.value = False
        self.state_2_on = False
    '''

    def start(self):
        """Start event system and own cyclic loop."""

        # Start event system without blocking here
        self.rpi.mainloop(blocking=False)

        # My own loop to do some work next to the event system. We will stay
        # here till self.rpi.exitsignal.wait returns True after SIGINT/SIGTERM
        while not self.rpi.exitsignal.wait(5):

            print("remote_controlled: ", self.remote_controlled, " remote_1: ", self.rpi.io.remote_1.value)

            # Switch on / off green part of LED A1 to signal user that PLC runs
            self.rpi.core.a1green.value = not self.rpi.core.a1green.value
            # if remote output (used as memory) are turnon/off, do
            # note monitoring en setting of output with event action didn't worked
            if self.remote_controlled:
                if self.rpi.io.remote_1.value:
                    if not self.state_2_on:
                        self.rpi.io.relay_1.value = True
                        self.state_1_on = True
                else:
                    self.rpi.io.relay_1.value = False
                    self.state_1_on = False

                if self.rpi.io.remote_2.value:
                    if not self.state_1_on:
                        self.rpi.io.relay_2.value = True
                        self.state_2_on = True
                else:
                    self.rpi.io.relay_2.value = False
                    self.state_2_on = False


if __name__ == "__main__":
    # Start RevPiApp app
    root = MyRevPiApp()
    root.start()
