#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) EJSol 8 jun 2019 minimal text demo based on Rev-local-switch-pyload-v1 of 3 jan
# main_switch, switch_1 and switch_2, main_relay, etc input/output are all defined in Kunbus piCtory

import revpimodio2

rpi = revpimodio2.RevPiModIO(autorefresh=True)

main_state = False
state_1 = False
state_2 = False


def main():

    global main_state, state_1, state_2

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
        global state_1
        rpi.io.relay_1.value = False
        state_1 = False

    def event_switch_2_on(ioname, iovalue):
        global main_state, state_1, state_2
        if main_state and not state_1:
            rpi.io.relay_2.value = True
            state_2 = True

    def event_switch_2_off(ioname, iovalue):
        global state_2
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

    rpi.io.main_relay.value = False
    rpi.io.relay_1.value = False
    rpi.io.relay_2.value = False
    revpimodio2.RevPiModIO(autorefresh=False)


if __name__ == '__main__':
    main()
