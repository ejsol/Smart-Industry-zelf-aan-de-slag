#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) EJSol 17 jul 2019 freeware for use in Smart Industry - Zelf Aan de Slag workshop (SIZAS)
#
# start control program and run opc-ua server from command line and
# use from other computer opc client to read data from this opc server
# run $python3 Rev-demo-... or after making it executable (chmod +x Rev*) using: ./Rev-demo-..
# check after killing it with: ps -ae is process has stopped, else get the process id (pid) and: sudo kill -HUP pid
#
# main_switch, switch_1 and switch_2, main_relay, etc input/output are all defined in Kunbus piCtory
#
# piCtory Setup: RevPICore | DIO
#
# I/O RevPi name    OPC name
# I_1 main_switch   warehouse
# I_3 switch_1      door_outside
# I_5 switch_2      door_inside
#
# O_1 main_relay    warehouse
# O_3 relay_1       door_outside
# O_5 relay_2       door_inside
#
# states: main_state determined by main_switch, if turned on main_relay is powered ON and main_state is true
#         state_1 is status of outside door, switch_1/relay_1
#         state_2 is status of inside door, switch_2/relay_2
#
# A1green LED indicates running program, A2red indicated system is on (main_switch on, main_state = True)
#

import time
import datetime
from opcua import Server
import revpimodio2


class MyRevPiOpcuaServerApp:

    def __init__(self):

        """Init MyRevPiApp class."""
        
        self.main_state = False
        self.state_1_on = False
        self.state_2_on = False
        self.trigger = 0
        self.trigger_system_on_trigger = 1
        self.trigger_system_off_trigger = 2
        self.trigger_door_outside_open = 3
        self.trigger_door_outside_close = 4
        self.trigger_door_inside_open = 5
        self.trigger_door_inside_close = 6

        self.system_on_time = 0.0
        self.system_off_time = 0.0
        self.system_delta_time = 0.0
        self.system_running_time = 0.0
        self.system_sum_time = 0.0
        self.door_count = 0
        self.door_outside_time_opened = 0.0
        self.door_outside_time_closed = 0.0
        self.door_outside_delta_time_open = 0.0
        self.door_outside_sum_time_open = 0.0
        self.door_inside_time_opened = 0.0
        self.door_inside_time_closed = 0.0
        self.door_inside_delta_time_open = 0.0
        self.door_inside_sum_time_open = 0.0
        self.open_percentage = 0
        self.door_open_time = 0.0
        self.door_outside_share_percentage = 50     # = door_outside/(door_outside+door_inside)time

        print("put all switches in off mode")

        # Instantiate RevPiModIO
        self.rpi = revpimodio2.RevPiModIO(autorefresh=True)
        # standard cycletime on Core-3 is 20 (msec), by uncommenting next line you extend it to 50 msec
        # might be needed if once more print statements are used in event handlers
        # self.rpi.cycletime = 50

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

        print('starting OPC server . (url 10.0.0.3:4840)')
        self.opc_server = Server(shelffile="/home/pi/RevPi-OPC-Server")
        self.opc_url = "opc.tcp://10.0.0.3:4840"
        self.opc_server.set_endpoint(self.opc_url)
        # TODO security
        print('starting OPC server .. (namespace)')
        self.opc_name = "RevPi-opcua-server"
        self.addspace = self.opc_server.register_namespace(self.opc_name)
        print('starting OPC server ... (variables)')
        self.opc_node = self.opc_server.get_objects_node()
        self.param = self.opc_node.add_object(self.addspace, "Parameters")

        self.opc_time = self.param.add_variable(self.addspace, "Time", 0)                                # opc i=2
        self.opc_trigger = self.param.add_variable(self.addspace, "Trigger", 0)                          # opc i=3
        self.opc_warehouse_state = self.param.add_variable(self.addspace, "System state", 0)             # opc i=4
        self.opc_door_outside = self.param.add_variable(self.addspace, "Outside door", 0)                # opc i=5
        self.opc_door_inside = self.param.add_variable(self.addspace, "Inside door", 0)                  # opc i=6
        self.opc_open_percentage = self.param.add_variable(self.addspace, "Door open %", 0.0)  # opc i=7
        self.opc_door_outside_share_percentage = self.param.add_variable(self.addspace, "Outside/Inside share", 0.0)

        self.opc_time.set_writable()
        self.opc_trigger.set_writable()
        self.opc_warehouse_state.set_writable()
        self.opc_door_outside.set_writable()
        self.opc_door_inside.set_writable()
        self.opc_open_percentage.set_writable()
        self.opc_door_outside_share_percentage.set_writable()

        self.opc_server.start()
        print("OPC UA Server started at {}".format(self.opc_url))

    def cleanup_revpi(self):
        """Cleanup function to leave the RevPi in a defined state, stop opc server and exit."""
        self.rpi.core.a1green.value = False
        self.rpi.core.a1red.value = False
        self.rpi.io.main_relay.value = False
        self.rpi.io.relay_1.value = False
        self.rpi.io.relay_2.value = False
        self.rpi = revpimodio2.RevPiModIO(autorefresh=False)
        self.opc_server.stop()
        print("exit")
        # self.master.destroy()
        exit(1)

    def event_main_on(self, ioname, iovalue):
        """Called if main_switch goes to True."""
        # Switch on/off output O_1
        self.rpi.io.main_relay.value = True
        self.main_state = True
        self.system_on_time = time.time()
        self.trigger = self.trigger_system_on_trigger

    def event_main_off(self, ioname, iovalue):
        """Called if main_switch goes to false."""
        # Switch on/off output O_1
        self.rpi.io.main_relay.value = False
        self.rpi.io.relay_1.value = False
        self.rpi.io.relay_2.value = False
        self.main_state = False
        self.system_off_time = time.time()
        self.system_delta_time = self.system_off_time - self.system_on_time
        self.system_sum_time = self.system_sum_time + self.system_delta_time
        print("system  delta: ", int(self.system_delta_time), "sec    system  sum: ", int(self.system_sum_time), ' sec')

        if self.state_1_on:
            self.door_outside_time_closed = time.time()
            self.door_outside_delta_time_open = self.door_outside_time_closed - self.door_outside_time_opened
            self.door_outside_sum_time_open = self.door_outside_sum_time_open + self.door_outside_delta_time_open
        elif self.state_2_on:
            self.door_inside_time_closed = time.time()
            self.door_inside_delta_time_open = self.door_inside_time_closed - self.door_inside_time_opened
            self.door_inside_sum_time_open = self.door_inside_sum_time_open + self.door_inside_delta_time_open
        self.trigger = self.trigger_system_off_trigger

    def event_switch_1_on(self, ioname, iovalue):
        """Called if I_3 goes to True."""
        if self.main_state and not self.state_2_on:
            self.rpi.io.relay_1.value = True
            self.state_1_on = True
            self.door_outside_time_opened = time.time()
            self.trigger = self.trigger_door_outside_open

    def event_switch_1_off(self, ioname, iovalue):
        """Called if I_3 goes to false."""
        if self.main_state:
            self.rpi.io.relay_1.value = False
            self.state_1_on = False
            self.door_count = self.door_count + 1
            # self.door_outside_time_closed = time.time()
            # self.door_outside_delta_time_open = self.door_outside_time_closed - self.door_outside_time_opened
            # self.door_outside_sum_time_open = self.door_outside_sum_time_open + self.door_outside_delta_time_open
            # print("outside delta: ", int(self.door_outside_delta_time_open),
            #       "sec    outside sum: ", int(self.door_outside_sum_time_open), ' sec')
            self.door_outside_sum_time_open = self.door_outside_sum_time_open + time.time() - self.door_outside_time_opened
            self.trigger = self.trigger_door_outside_close

    def event_switch_2_on(self, ioname, iovalue):
        """Called if I_5 goes to True."""
        if self.main_state and not self.state_1_on:
            self.rpi.io.relay_2.value = True
            self.state_2_on = True
            self.door_inside_time_opened = time.time()
            self.trigger = self.trigger_door_inside_open

    def event_switch_2_off(self, ioname, iovalue):
        """Called if I_5 goes to False."""
        if self.main_state:
            self.rpi.io.relay_2.value = False
            self.state_2_on = False
            self.door_count = self.door_count + 1
            # self.door_inside_time_closed = time.time()
            # self.door_inside_delta_time_open = self.door_inside_time_closed - self.door_inside_time_opened
            # self.door_inside_sum_time_open = self.door_inside_sum_time_open + self.door_inside_delta_time_open
            # print("inside  delta: ", int(self.door_inside_delta_time_open),
            #       "sec     inside  sum: ", int(self.door_inside_sum_time_open), ' sec')
            self.door_inside_sum_time_open = self.door_inside_sum_time_open + time.time() - self.door_inside_time_opened
            self.trigger = self.trigger_door_inside_close

    def start(self):
        """Start event system and own cyclic loop."""

        # Start event system without blocking here
        self.rpi.mainloop(blocking=False)

        # My own loop to do some work next to the event system. We will stay
        # here till self.rpi.exitsignal.wait returns True after SIGINT/SIGTERM
        while not self.rpi.exitsignal.wait(1):

            # Switch on / off green part of LED A1 to signal to user that PLC runs
            self.rpi.core.a1green.value = not self.rpi.core.a1green.value
            self.opc_time.set_value(datetime.datetime.now())
            self.opc_trigger.set_value(self.trigger)
            if self.trigger == self.trigger_system_on_trigger or self.trigger == self.trigger_system_off_trigger:
                self.opc_warehouse_state.set_value(self.main_state)
            if self.trigger == self.trigger_door_outside_open or self.trigger == self.trigger_door_outside_close:
                self.opc_door_outside.set_value(self.state_1_on)
            if self.trigger == self.trigger_door_inside_open or self.trigger == self.trigger_door_inside_close:
                self.opc_door_inside.set_value(self.state_2_on)

            # needed to update system on time while no event takes place
            if self.main_state:
                self.system_delta_time = time.time() - self.system_on_time
                self.system_running_time = self.system_sum_time + self.system_delta_time
            else:
                self.system_running_time = self.system_sum_time

            self.door_open_time = self.door_outside_sum_time_open + self.door_inside_sum_time_open

            if self.system_running_time == 0.0:  # if 0 then main has not been switched on yet
                self.open_percentage = 0
            else:
                self.open_percentage = (self.door_open_time / self.system_running_time) * 100
            # print("door open time: ", int(self.door_open_time),
            #       " system on time: ", int(self.system_running_time), ' sec')

            if self.door_open_time == 0.0:  # if 0 then main has not been switched on yet
                self.door_outside_share_percentage = 50  # if 0, avoid DIV by Zero, and start at 50/50%
            else:
                self.door_outside_share_percentage = (self.door_outside_sum_time_open / self.door_open_time) * 100

            self.opc_open_percentage.set_value(self.open_percentage)
            self.opc_door_outside_share_percentage.set_value(self.door_outside_share_percentage)

    # TODO
    #  add keyboard interupt as in
    # try:
    #       time.sleep(5)
    #       self.update_opc(0)
    #    except KeyboardInterrupt:
    #        self.closeapp()


if __name__ == '__main__':
    myapp = MyRevPiOpcuaServerApp()
    myapp.start()
