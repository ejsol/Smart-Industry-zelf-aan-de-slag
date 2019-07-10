#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) EJSol 8 jun 2019 freeware for use in Smart Industry - Zelf Aan de Slag workshop (SIZAS)
#
# to be used with MQTT broker on 10.0.0.4 (Pi-4 next to RevPi (RevPi on same 10.0.0.0/24 subnet)
# note in RevPi MQTT setting broker is now on 10.0.0.4, but can be on localhost too
# in case of broker on localhost, change line 293 broker = "localhost"
#
# first check that no other PLC program is running on the RevPi, (e.g. with RevPiPyControl, stop running PLC prog.)
# start this program on Pi-4, it will control the I/O on the RevPi,
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
import paho.mqtt.client as mqtt
import time
import logging


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
        self.btn_main_on["command"] = self.main_on
        self.btn_main_on.grid(row=1, column=0)

        self.btn_door_1_open = Button(self.master, text="Open Outside Door", width=15)
        self.btn_door_1_open["command"] = self.button_1_on
        self.btn_door_1_open.grid(row=1, column=1)

        self.btn_door_2_open = Button(self.master, text="Open Inside Door", width=15)
        self.btn_door_2_open["command"] = self.button_2_on
        self.btn_door_2_open.grid(row=1, column=2)

        self.lbl_energy = Label(self.master, text="loss: " + str(int(self.door_open_time)), width=15, height=4)
        self.lbl_energy.grid(row=1, column=3)

        # Status information in middle row

        self.lbl_state_main = Label(self.master, bg='light grey', text="OFF", width=15, height=4)
        self.lbl_state_main.grid(row=2, column=0)

        self.lbl_state_door_1 = Label(self.master, bg='light grey', text="Closed", width=15, height=4)
        self.lbl_state_door_1.grid(row=2, column=1)

        self.lbl_state_door_2 = Label(self.master, bg='light grey', text="Closed", width=15, height=4)
        self.lbl_state_door_2.grid(row=2, column=2)

        self.lbl_count = Label(self.master, text="# door: " + str(int(self.door_count)), width=15)
        self.lbl_count.grid(row=2, column=3)

        # bottom row with switches (buttons) in off state (black button grayed in on)

        self.btn_main_off = Button(self.master, text="Turn System Off", width=15)
        self.btn_main_off.config(bg='#00C1FF', fg='white')
        self.btn_main_off["command"] = self.main_off
        self.btn_main_off.grid(row=3, column=0)

        self.btn_door_1_close = Button(self.master, text="Close Outside Door", width=15)
        self.btn_door_1_close.config(bg='#00C1FF', fg='white')
        self.btn_door_1_close["command"] = self.button_1_off
        self.btn_door_1_close.grid(row=3, column=1)

        self.btn_door_2_close = Button(self.master, text="Close Inside Door", width=15)
        self.btn_door_2_close.config(bg='#00C1FF', fg='white')
        self.btn_door_2_close["command"] = self.button_2_off
        self.btn_door_2_close.grid(row=3, column=2)

        self.lbl_system_on = Label(self.master, text="time on:" + str(int(self.system_on_time)), width=15)
        self.lbl_system_on.grid(row=3, column=3)

        self.btn_stop = Button(self.master, text="Stop")
        self.btn_stop["command"] = self.closeapp
        self.btn_stop.grid(row=4, column=0)

    def closeapp(self):
        self.master.destroy()

    def main_on(self):
        self.main_state = True
        self.system_on = time.time()
        self.btn_main_on.config(bg='#00CC00', fg='white')
        self.lbl_state_main.config(bg='#00CC00', text="ON")
        self.btn_main_off.config(bg='white', fg='black')
        logging.info("publish")
        ret = client.publish("revpi/set/main_relay", 1, 0)
        logging.info("published return=" + str(ret))

    def main_off(self):
        self.main_state = False
        self.door_1_state = False
        self.door_2_state = False

        self.btn_main_on.config(bg='#EAEAEA', fg='black')
        self.lbl_state_main.config(bg='light grey', text="Off")
        self.btn_main_off.config(bg='#00C1FF', fg='white')

        # self.system_delta_time = time.time() - self.system_on
        # self.system_on_time = self.system_on_time + self.system_delta_time
        self.system_on_time = self.system_on_time + time.time() - self.system_on
        self.lbl_system_on.config(text="time on:" + str(int(self.system_on_time)))
        self.lbl_energy.config(text="loss: " + str(int(self.door_open_time)))
        self.lbl_count.config(text="# door: " + str(int(self.door_count)))

        client.publish("revpi/set/main_relay", 0, 0)
        client.publish("revpi/set/relay_1", 0, 0)
        client.publish("revpi/set/relay_2", 0, 0)

    def button_1_on(self):
        if self.main_state:
            if not self.door_2_state:
                self.door_1_state = True
                self.btn_door_1_open.config(bg='#FF0000', fg='white')
                self.lbl_state_door_1.config(bg='#FF0000', text="Open")
                self.btn_door_1_close.config(bg='white', fg='black')

                self.door_time = time.time()
                client.publish("revpi/set/relay_1", 1, 0)

    def button_1_off(self):
        if self.main_state:
            self.door_1_state = False
            self.btn_door_1_open.config(bg='#EAEAEA', fg='black')
            self.lbl_state_door_1.config(bg='light grey', text="Closed")
            self.btn_door_1_close.config(bg='#00C1FF', fg='white')

            self.door_count = self.door_count + 1
            self.lbl_count.config(text="# door: " + str(int(self.door_count)))
            self.door_open_time = self.door_open_time + time.time() - self.door_time
            self.lbl_energy.config(text="loss: " + str(int(self.door_open_time)))

            client.publish("revpi/set/relay_1", 0, 0)

    def button_2_on(self):
        if self.main_state:
            if not self.door_1_state:
                self.door_2_state = True
                self.btn_door_2_open.config(bg='#FF0000', fg='white')
                self.lbl_state_door_2.config(bg='#FF0000', text="Open")
                self.btn_door_2_close.config(bg='white', fg='black')

                self.door_time = time.time()
                client.publish("revpi/set/relay_2", 1, 0)

    def button_2_off(self):
        if self.main_state:
            self.door_2_state = False
            self.btn_door_2_open.config(bg='#EAEAEA', fg='black')
            self.lbl_state_door_2.config(bg='light grey', text="Closed")
            self.btn_door_2_close.config(bg='#00C1FF', fg='white')

            self.door_count = self.door_count + 1
            self.lbl_count.config(text="# door: " + str(int(self.door_count)))

            self.door_open_time = self.door_open_time + time.time() - self.door_time
            self.lbl_energy.config(text="loss: " + str(int(self.door_open_time)))
            client.publish("revpi/set/relay_2", 0, 0)


def on_log(client, userdata, level, buf):
    logging.info(buf)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True
        logging.info("connected OK")
    else:
        logging.info("bad connection, return code rc:" + str(rc))
        client.loop_stop()


def on_disconnect(client, userdata, rc):
    logging.info("client disconnected OK")


def on_publish(client, userdata, mid):
    logging.info("In on_pub callback mid " + str(mid))


def on_subscribe(client, userdata, mid, granted_qos):
    logging.info("subscribed")


def on_message(client, userdata, message):
    global count_state, main_count, main_count_delta, energy_loss
    global door_1_count, door_1_count_delta
    global door_2_count, door_2_count_delta

    # TODO I use here variable with a global scope als call-back routine can't pass parameters
    #  but instance variable might be better

    # topic = message.topic
    # [ data , measurement,  text   ,   sensorname ]
    # ["data",  "revpi" ,  "event"   , "main_switch"]
    topics = message.topic.split("/")

    logging.info("on_message " + str(topics))

    # als geen drie elementen, dan verwerpen
    if len(topics) != 3:
        return

    if topics[1] == 'event':
        if topics[2] == 'main_relay':
            if int(message.payload) == 0:
                count_state = False
                main_count = main_count + time.time() - main_count_delta
                print('door open/closed: # ', main_count)
            else:
                count_state = True
                main_count_delta = time.time()
        elif topics[2] == 'relay_1':
            if int(message.payload) == 0:
                # door_1_state = False
                delta = time.time() - door_1_count_delta
                if delta < 10:
                    door_1_count = door_1_count + delta
                else:
                    door_1_count = door_1_count + 10
                energy_loss = int(door_1_count + door_2_count)
                print('energy loss due to opening of doors: ', energy_loss)
                # energy_loss_label["text"] = energy_loss
            else:
                # door_1_state = True
                door_1_count_delta = time.time()
        elif topics[2] == 'relay_2':
            if int(message.payload) == 0:
                # door_2_state = False
                delta = time.time() - door_2_count_delta
                if delta < 10:
                    door_2_count = door_2_count + delta
                else:
                    door_2_count = door_2_count + 10
                energy_loss = int(door_1_count + door_2_count)
                print('energy loss due to opening of doors: ', energy_loss)
                # energy_loss_label["text"] = energy_loss
            else:
                # door_2_state = True
                door_2_count_delta = time.time()
        else:
            return


if __name__ == '__main__':

    broker = "10.0.0.4"
    # TODO put broker IP in program entry
    port = 1883
    logging.basicConfig(level=logging.INFO)
    # user DEBUG, INFO, WARNING

    count_state = False
    main_count = 0
    main_count_delta = 0
    energy_loss = 0
    door_1_state = False
    door_1_count = 0
    door_1_count_delta = 0
    door_2_state = False
    door_2_count = 0
    door_2_count_delta = 0

    mqtt.Client.connected_flag = False
    # opmerkelijk, vlag wordt gezet voor dat object wordt aan gemaakt, uit steve cope
    # maar truc is om de client object uit te rusten met extra variables die niet met callback terug komen

    # TODO class voor een object waar binnen the parameter/variable and object object-scope instead of system
    #   still need to figure out how to deal with the screen object in a MQTT object.

    client = mqtt.Client("test")
    # Client client_id, clean_session, userdata=none, protocol MQTTv3
    client.username_pw_set(username="smart", password="industry")

    client.on_log = on_log
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    client.connect(broker, port)
    client.subscribe("revpi/event/main_relay", 0)
    client.subscribe("revpi/event/relay_1", 0)
    client.subscribe("revpi/event/relay_2", 0)

    client.loop_start()

    while not client.connected_flag:
        logging.info("in wait loop for MQTT connection" + str(broker))
        time.sleep(1)

    root = Tk()
    MyRevPiApp(root).mainloop()

    client.loop_stop()
    client.disconnect()
