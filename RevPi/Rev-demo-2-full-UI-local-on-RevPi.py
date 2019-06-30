#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) EJSol 1 jul 2019 freeware for use in Smart Industry - Zelf Aan de Slag workshop (SIZAS)
#
# to be run from the windows user interface in terminal with python3 Rev-demo-2-full-UI-localon-RevPi.py
# or if made executable (chmod +x Rev...) with: ./Rev-...
# only run this file after the Rev-2 has been put in WINDOWS mode (after a: startx)
# do not run it from remote RevPiPyControl if Rev-2 is in CLI mode (the normal mode)
#
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
import time


class MyRevPiApp(Frame):

    def __init__(self, master=None):

        self.main_state = False
        self.door_1_state = False
        self.door_2_state = False
        self.door_count = 0
        self.system_on_time = 0
        self.system_on = 0
        self.system_delta_time = 0
        self.door_open_time = 0
        self.door_time = 0

        # Instantiate RevPiModIO
        self.rpi = revpimodio2.RevPiModIO(autorefresh=True)

        # Handle SIGINT / SIGTERM to exit program cleanly
        self.rpi.handlesignalend(self.closeapp)

        # Register event to toggle output O_1 with input I_1
        self.rpi.io.main_switch.reg_event(self.event_main_switch_on, edge=revpimodio2.RISING)
        self.rpi.io.main_switch.reg_event(self.event_main_switch_off, edge=revpimodio2.FALLING)

        # Register event to toggle output O_3 with input I_3
        self.rpi.io.switch_1.reg_event(self.event_switch_1_on, edge=revpimodio2.RISING)
        self.rpi.io.switch_1.reg_event(self.event_switch_1_off, edge=revpimodio2.FALLING)

        # Register event to toggle output O_5 with input I_5
        self.rpi.io.switch_2.reg_event(self.event_switch_2_on, edge=revpimodio2.RISING)
        self.rpi.io.switch_2.reg_event(self.event_switch_2_off, edge=revpimodio2.FALLING)

        self.rpi.core.a1green.value = False
        self.rpi.io.main_relay.value = False
        self.rpi.io.relay_1.value = False
        self.rpi.io.relay_2.value = False

        # Start RevPi event system without blocking here
        self.rpi.mainloop(blocking=False)

        # Handle tkinter part
        super().__init__(master)
        self.master.protocol("WM_DELETE_WINDOW", self.closeapp)

        self.master.wm_title("Warehouse")
        self.master.wm_resizable(width=False, height=False)
        fontlabel = ('helvetica', 15, 'bold')

        # top row names

        self.lbl_main = Label(self.master, text="System", width=15, font=fontlabel)
        self.lbl_main.grid(row=0, column=0)

        self.lbl_door_1 = Label(self.master, text="Outside Door", width=15, font=fontlabel)
        self.lbl_door_1.grid(row=0, column=1)

        self.lbl_door_2 = Label(self.master, text="Inside Door", width=15, font=fontlabel)
        self.lbl_door_2.grid(row=0, column=2)

        self.lbl_info = Label(self.master, text="Data", width=15, font=fontlabel)
        self.lbl_info.grid(row=0, column=3)

        # top row with switches (buttons) in on state (red, grayed in off mode)

        self.btn_main_on = Button(self.master, text="Turn System On", width=15)
        # only screen control after physical switch (event_main_switch) is turned on, then button is also active
        # self.btn_main_on["command"] = self.event_button_main_on
        self.btn_main_on.grid(row=1, column=0)

        self.btn_door_1_open = Button(self.master, text="Open Outside Door", width=15)
        self.btn_door_1_open["command"] = self.event_button_open_door_1
        self.btn_door_1_open.grid(row=1, column=1)

        self.btn_door_2_open = Button(self.master, text="Open Inside Door", width=15)
        self.btn_door_2_open["command"] = self.event_button_open_door_2
        self.btn_door_2_open.grid(row=1, column=2)

        self.lbl_energy = Label(self.master, text="loss: 0", width=15, height=4)
        self.lbl_energy.grid(row=1, column=3)

        # Status information in middle row

        self.lbl_state_main = Label(self.master, bg='light grey', text="OFF", width=15, height=4)
        self.lbl_state_main.grid(row=2, column=0)

        self.lbl_state_door_1 = Label(self.master, bg='light grey', text="Closed", width=15, height=4)
        self.lbl_state_door_1.grid(row=2, column=1)

        self.lbl_state_door_2 = Label(self.master, bg='light grey', text="Closed", width=15, height=4)
        self.lbl_state_door_2.grid(row=2, column=2)

        self.lbl_count = Label(self.master, text="# door: 0", width=15)
        self.lbl_count.grid(row=2, column=3)

        # bottom row with switches (buttons) in off state (black button grayed in on)

        self.btn_main_off = Button(self.master, text="Turn System Off", width=15)
        self.btn_main_off.config(bg='#00C1FF', fg='white')
        self.btn_main_off["command"] = self.event_button_main_off
        self.btn_main_off.grid(row=3, column=0)

        self.btn_door_1_close = Button(self.master, text="Close Outside Door", width=15)
        self.btn_door_1_close.config(bg='#00C1FF', fg='white')
        self.btn_door_1_close["command"] = self.event_button_close_door_1
        self.btn_door_1_close.grid(row=3, column=1)

        self.btn_door_2_close = Button(self.master, text="Close Inside Door", width=15)
        self.btn_door_2_close.config(bg='#00C1FF', fg='white')
        self.btn_door_2_close["command"] = self.event_button_close_door_2
        self.btn_door_2_close.grid(row=3, column=2)

        self.lbl_system_on = Label(self.master, text="time on: 0", width=15)
        self.lbl_system_on.grid(row=3, column=3)

        self.btn_stop = Button(self.master, text="Stop")
        self.btn_stop["command"] = self.closeapp
        self.btn_stop.grid(row=4, column=3)

    def closeapp(self):
        # tkinker
        self.master.destroy()

        # Switch off LED and outputs to leave RevPi in defined state before exit program
        self.rpi.core.a1green.value = False
        self.rpi.io.main_relay.value = False
        self.rpi.io.relay_1.value = False
        self.rpi.io.relay_2.value = False

        self.rpi = revpimodio2.RevPiModIO(autorefresh=False)

        self.main_state = False
        self.door_1_state = False
        self.door_2_state = False

    def event_main_switch_on(self, ioname, iovalue):
        """Called if main_switch (or from UI system button) goes to True."""
        self.main_state = True
        self.system_on = time.time()
        self.btn_main_on.config(bg='#00CC00', fg='white')
        self.lbl_state_main.config(bg='#00CC00', text="ON")
        self.btn_main_off.config(bg='white', fg='black')

        self.rpi.io.main_relay.value = True
        self.rpi.io.relay_1.value = False
        self.rpi.io.relay_2.value = False

    def event_main_switch_off(self, ioname, iovalue):
        """Called if main_switch (or UI system button) goes to False."""
        self.main_state = False
        self.btn_main_on.config(bg='#EAEAEA', fg='black')
        self.lbl_state_main.config(bg='light grey', text="Off")
        self.btn_main_off.config(bg='#00C1FF', fg='white')

        self.door_1_state = False
        self.btn_door_1_open.config(bg='#EAEAEA', fg='black')
        self.lbl_state_door_1.config(bg='light grey', text="Closed")
        self.btn_door_1_close.config(bg='#00C1FF', fg='white')

        self.door_2_state = False
        self.btn_door_2_open.config(bg='#EAEAEA', fg='black')
        self.lbl_state_door_2.config(bg='light grey', text="Closed")
        self.btn_door_2_close.config(bg='#00C1FF', fg='white')

        # self.system_delta_time = time.time() - self.system_on
        # self.system_on_time = self.system_on_time + self.system_delta_time
        self.system_on_time = self.system_on_time + time.time() - self.system_on
        self.lbl_system_on.config(text="time on:" + str(int(self.system_on_time)))
        self.lbl_energy.config(text="loss: " + str(int(self.door_open_time)))
        self.lbl_count.config(text="# door: " + str(int(self.door_count)))

        # Switch off output O_1
        self.rpi.io.main_relay.value = False
        self.rpi.io.relay_1.value = False
        self.rpi.io.relay_2.value = False

    def event_switch_1_on(self, ioname, iovalue):
        """Called if I_1 goes to True."""
        if self.main_state and not self.door_1_state:
            if not self.door_2_state:
                self.door_1_state = True
                self.btn_door_1_open.config(bg='#FF0000', fg='white')
                self.lbl_state_door_1.config(bg='#FF0000', text="Open")
                self.btn_door_1_close.config(bg='white', fg='black')

                self.door_time = time.time()
                self.rpi.io.relay_1.value = True

    def event_switch_1_off(self, ioname, iovalue):
        """Called if I_1 goes to False."""
        if self.main_state and self.door_1_state:
            self.door_1_state = False
            self.btn_door_1_open.config(bg='#EAEAEA', fg='black')
            self.lbl_state_door_1.config(bg='light grey', text="Closed")
            self.btn_door_1_close.config(bg='#00C1FF', fg='white')

            self.door_count = self.door_count + 1
            self.lbl_count.config(text="# door: " + str(int(self.door_count)))
            self.door_open_time = self.door_open_time + time.time() - self.door_time
            self.lbl_energy.config(text="loss: " + str(int(self.door_open_time)))

            self.rpi.io.relay_1.value = False

    def event_switch_2_on(self, ioname, iovalue):
        """Called if I_1 goes to True."""
        if self.main_state and not self.door_2_state:
            if not self.door_1_state:
                self.door_2_state = True
                self.btn_door_2_open.config(bg='#FF0000', fg='white')
                self.lbl_state_door_2.config(bg='#FF0000', text="Open")
                self.btn_door_2_close.config(bg='white', fg='black')

                self.door_time = time.time()
                self.rpi.io.relay_2.value = True

    def event_switch_2_off(self, ioname, iovalue):
        """Called if I_1 goes to False."""
        if self.main_state and self.door_2_state:
            self.door_2_state = False
            self.btn_door_2_open.config(bg='#EAEAEA', fg='black')
            self.lbl_state_door_2.config(bg='light grey', text="Closed")
            self.btn_door_2_close.config(bg='#00C1FF', fg='white')

            self.door_count = self.door_count + 1
            self.lbl_count.config(text="# door: " + str(int(self.door_count)))

            self.door_open_time = self.door_open_time + time.time() - self.door_time
            self.lbl_energy.config(text="loss: " + str(int(self.door_open_time)))
            self.rpi.io.relay_2.value = False
    '''
    def event_button_main_on(self):
        self.event_main_switch_on(self.rpi.io.main_switch.name, True)
    '''
    def event_button_main_off(self):
        self.event_main_switch_off(self.rpi.io.main_switch.name, False)

    def event_button_open_door_1(self):
        self.event_switch_1_on(self.rpi.io.switch_1.name, True)

    def event_button_close_door_1(self):
        self.event_switch_1_off(self.rpi.io.switch_1.name, False)

    def event_button_open_door_2(self):
        self.event_switch_2_on(self.rpi.io.switch_2.name, True)

    def event_button_close_door_2(self):
        self.event_switch_2_off(self.rpi.io.switch_2.name, False)


if __name__ == '__main__':
    root = Tk()
    MyRevPiApp(root).mainloop()
