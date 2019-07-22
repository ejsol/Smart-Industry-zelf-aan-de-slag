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
import revpimodio2
from opcua import Server


class MyRevPiOpcuaServerApp:

    def __init__(self):

        """Init MyRevPiApp class."""
        
        self.main_state = False
        self.state_1_on = False
        self.state_2_on = False
        self.system_on_time = 0
        self.system_on = 0
        self.system_delta_time = 0
        self.door_count = 0
        self.door_outside_open_time = 0
        self.door_outside_time = 0
        self.door_inside_open_time = 0
        self.door_inside_time = 0
        self.open_percentage = 0
        self.door_open_time = 0
        self.door_outside_share_percentage = 50   # = door_outside/(door_outside+door_inside)time
        
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


        print('starting OPC server ')
        self.opc_server = Server()
        self.opc_url = "opc.tcp://10.0.0.5:4840"
        self.opc_server.set_endpoint(self.opc_url)
        print('starting OPC server ..')
        self.opc_name = "RevPi-opcua-server"
        self.addspace = self.opc_server.register_namespace(self.opc_name)
        print('starting OPC server ...')
        self.opc_node = self.opc_server.get_objects_node()
        self.param = self.opc_node.add_object(self.addspace, "Parameters")

        self.opc_time = self.param.add_variable(self.addspace, "Time", 0)
        self.opc_trigger = self.param.add_variable(self.addspace, "Trigger", 0)
        self.opc_warehouse_state = self.param.add_variable(self.addspace, "System state", 0)
        self.opc_door_outside = self.param.add_variable(self.addspace, "Outside door", 0)
        self.opc_door_inside = self.param.add_variable(self.addspace, "Inside door", 0)
        self.opc_open_percentage = self.param.add_variable(self.addspace, "Open/Close percentage", 0)
        self.opc_door_outside_share_percentage = self.param.add_variable(self.addspace, "Outside/Inside share")

        self.opc_time.set_writable()
        self.opc_trigger.set_writable()
        self.opc_warehouse_state.set_writable()
        self.opc_door_outside.set_writable()
        self.opc_door_inside.set_writable()
        self.opc_open_percentage.set_writeable()
        self.opc_door_outside_share_percentage.set_writeable()

        print('starting OPC server .....')
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

    def update_opc(self, trigger):
        self.opc_time.set_value(datetime.datetime.now())
        self.opc_trigger.set_value(trigger)
        self.opc_warehouse_state.set_value(self.main_state)
        self.opc_door_outside.set_value(self.state_1_on)
        self.opc_door_inside.set_value(self.state_2_on)

        self.door_open_time = self.door_outside_open_time + self.door_inside_open_time
        self.open_percentage = (self.door_open_time/self.system_on_time)*100
        self.door_outside_share_percentage = (self.door_outside_open_time/self.door_open_time)*100

        self.opc_open_percentage.set_value(self.open_percentage)
        self.opc_door_outside_share_percentage.set_value(self.door_outside_share_percentage)

    def event_main_on(self, ioname, iovalue):
        """Called if main_switch goes to True."""
        # Switch on/off output O_1
        self.rpi.core.a2red.value = True
        self.rpi.io.main_relay.value = True
        self.main_state = True
        self.system_on = time.time()
        self.update_opc(1)

    def event_main_off(self, ioname, iovalue):
        """Called if main_switch goes to false."""
        # Switch on/off output O_1
        self.rpi.io.main_relay.value = False
        self.rpi.io.relay_1.value = False
        self.rpi.io.relay_2.value = False
        self.rpi.core.a2red.value = False
        self.main_state = False
        self.system_on_time = self.system_on_time + time.time() - self.system_on
        self.door_outside_open_time = self.door_outside_open_time + time.time() - self.door_outside_time
        self.door_inside_open_time = self.door_inside_open_time + time.time() - self.door_inside_time
        self.update_opc(1)

    def event_switch_1_on(self, ioname, iovalue):
        """Called if I_3 goes to True."""
        if self.main_state and not self.state_2_on:
            self.rpi.io.relay_1.value = True
            self.state_1_on = True
            self.door_outside_time = time.time()
        self.update_opc(2)

    def event_switch_1_off(self, ioname, iovalue):
        """Called if I_3 goes to false."""
        self.rpi.io.relay_1.value = False
        self.state_1_on = False
        self.door_count = self.door_count + 1
        self.door_outside_open_time = self.door_outside_open_time + time.time() - self.door_outside_time
        self.update_opc(2)

    def event_switch_2_on(self, ioname, iovalue):
        """Called if I_5 goes to True."""
        if self.main_state and not self.state_1_on:
            self.rpi.io.relay_2.value = True
            self.state_2_on = True
            self.door_inside_time = time.time()
        self.update_opc(3)

    def event_switch_2_off(self, ioname, iovalue):
        """Called if I_5 goes to False."""
        self.rpi.io.relay_2.value = False
        self.state_2_on = False
        self.door_count = self.door_count + 1
        self.door_inside_open_time = self.door_inside_open_time + time.time() - self.door_inside_time
        self.update_opc(3)

    def start(self):
        """Start event system and own cyclic loop."""

        # Start event system without blocking here
        self.rpi.mainloop(blocking=False)

        # My own loop to do some work next to the event system. We will stay
        # here till self.rpi.exitsignal.wait returns True after SIGINT/SIGTERM
        while not self.rpi.exitsignal.wait(1):

            # Switch on / off green part of LED A1 to signal to user that PLC runs
            self.rpi.core.a1green.value = not self.rpi.core.a1green.value
            if self.main_state:
                self.rpi.core.a2red.value = not self.rpi.core.a2red.value
            self.update_opc(0)

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
