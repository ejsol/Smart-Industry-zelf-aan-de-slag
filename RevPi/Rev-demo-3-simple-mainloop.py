#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) EJSol 1 jul 2019 freeware for use in Smart Industry - Zelf Aan de Slag workshop (SIZAS)
#
# minimal text demo to be started with e.g. Revpipycontrol from remote RevPi Python Control on a other computer
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

import revpimodio2


def main():

    global main_state, state_1, state_2

    main_state = False
    state_1 = False
    state_2 = False

    rpi = revpimodio2.RevPiModIO(autorefresh=True)

    def event_main_on(ioname, iovalue):
        global main_state
        rpi.io.main_relay.value = True
        main_state = True

    def event_main_off(ioname, iovalue):
        global main_state
        rpi.io.main_relay.value = False
        rpi.io.relay_1.value = False
        rpi.io.relay_2.value = False
        main_state = False

    def event_switch_1_on(ioname, iovalue):
        global main_state, state_1, state_2
        if main_state and not state_2:
            rpi.io.relay_1.value = True
            state_1 = True

    def event_switch_1_off(ioname, iovalue):
        global main_state, state_1
        if main_state:
            rpi.io.relay_1.value = False
            state_1 = False

    def event_switch_2_on(ioname, iovalue):
        global main_state, state_1, state_2
        if main_state and not state_1:
            rpi.io.relay_2.value = True
            state_2 = True

    def event_switch_2_off(ioname, iovalue):
        global main_state, state_2
        if main_state:
            rpi.io.relay_2.value = False
            state_2 = False

    # Register event to main_switch, switch_1 and switch_2
    rpi.io.main_switch.reg_event(event_main_on, edge=revpimodio2.RISING)
    rpi.io.main_switch.reg_event(event_main_off, edge=revpimodio2.FALLING)

    rpi.io.switch_1.reg_event(event_switch_1_on, edge=revpimodio2.RISING)
    rpi.io.switch_1.reg_event(event_switch_1_off, edge=revpimodio2.FALLING)

    rpi.io.switch_2.reg_event(event_switch_2_on, edge=revpimodio2.RISING)
    rpi.io.switch_2.reg_event(event_switch_2_off, edge=revpimodio2.FALLING)

    # initialize output to False = 0 = off = no-lights
    rpi.io.main_relay.value = False
    rpi.io.relay_1.value = False
    rpi.io.relay_2.value = False

    rpi.mainloop(blocking=False)

    # We stay here, switch on the LED A1 every sec, till rpi.exitsignal.wait returns True after SIGINT/SIGTERM
    while not rpi.exitsignal.wait(1):
        rpi.core.a1green.value = not rpi.core.a1green.value

    # exit/terminate program and reset output to False
    rpi.io.main_relay.value = False
    rpi.io.relay_1.value = False
    rpi.io.relay_2.value = False
    revpimodio2.RevPiModIO(autorefresh=False)


if __name__ == '__main__':
    main()
