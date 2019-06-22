#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) EJSol 8 jun 2019 freeware for use in Smart Industry - Zelf Aan de Slag workshop (SIZAS)
#
# to be run from the windows user interface in terminal with python3 Rev-demo-1-bare-UI-local-on-RevPi.py
# main_switch, switch_1 and switch_2, main_relay, etc input/output are all defined in Kunbus piCtory
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

from tkinter import *
import revpimodio2


class MyRevPiApp(Frame):

    def __init__(self, master=None):
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
        self.rpi.io.main_relay.value = False   # O 1 (output 1) right side connector on DIO is odd input/output nr
        self.rpi.io.relay_1.value = False      # O 3
        self.rpi.io.relay_2.value = False      # O 5

        self.rpi.mainloop(blocking=False)

        self.main_state = False
        self.state_1_on = False
        self.state_2_on = False

        # Handle tkinter part
        super().__init__(master)
        self.master.protocol("WM_DELETE_WINDOW", self.cleanup_revpi)

        self.master.wm_title("plc program")
        self.master.wm_resizable(width=False, height=False)
        fontlabel = ('helvetica', 15, 'bold')
        self.btn_stop = Button(self.master, text="Stop running PLC program", font=fontlabel)
        self.btn_stop["command"] = self.cleanup_revpi
        self.btn_stop.grid(row=0, column=0)

    def cleanup_revpi(self):
        """Cleanup function to leave the RevPi in a defined state."""
        # Switch off LED and outputs before exit program
        self.rpi.core.a1green.value = False
        self.rpi.io.main_relay.value = False
        self.rpi.io.relay_1.value = False
        self.rpi.io.relay_2.value = False
        self.rpi = revpimodio2.RevPiModIO(autorefresh=False)
        # tkinker
        self.master.destroy()

    def event_main_on(self, ioname, iovalue):
        """Called if main_switch goes to True."""
        # Switch on/off output O_1
        self.rpi.core.a2red.value = False
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
        self.rpi.io.relay_1.value = False
        self.state_1_on = False

    def event_switch_2_on(self, ioname, iovalue):
        """Called if I_5 goes to True."""
        if self.main_state and not self.state_1_on:
            self.rpi.io.relay_2.value = True
            self.state_2_on = True

    def event_switch_2_off(self, ioname, iovalue):
        """Called if I_5 goes to False."""
        self.rpi.io.relay_2.value = False
        self.state_2_on = False


if __name__ == "__main__":
    root = Tk()
    MyRevPiApp(root).mainloop()
