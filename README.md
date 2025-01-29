
# Intro

These are the files are part of the Zelf-aan-de-Slag data & cyber security Smart Industry workshop. 
SIZAS stands for: Smart Industry Zelf Aan de Slag, or in English Smart Industry - Do It Yourself.

There are  PDF with the presentation and two participants instruction documents with all the needed
settings for the RevPi and the Pi sessions. Available upon request as github does not support such files (yet, I need to make markdown documents of them).
There is another document describing the hack cases. Not disclosuring the tricks to participants of the workshop, you can image that this document is not generally available.

The Python program files and instruction you can download from githubs using the command:

`git clone https://github.com/ejsol/Smart-Industry-zelf-aan-de-slag.git
`

## Workshop demonstration Revolution Pi's (the Python PLC)

To run the example code you find in the RevPi directory Rev-1 till Rev-3 to run on a RevPi (10.0.0.2 (Core 1 type)). The code Rev3-1 till Rev3-4-server your run on the Rev3 at 192.168.0.3 (Core 3 RevPi)) in the shielded smart-factory subnetwork
(see README in Network directory why we use such a subnet).

`python3 1-Rev-simple-mainloop-by-revpipycontrol.py`

Note: don't type the long names, just start typing the first letters of the program and type tab to complete the full name. Linux scan the current file directory for the name that completes it. 

You start the Rev programs from your own PC using RevPi Python Control program (revpipycontrol)
These programs requires that the RevPi runs the revpimodio2 service from www.revpimodio.org . If not, then on pi@RevPi enter the following command to start the revpipy service:

`
$ sudo service revpipyload start
`

The Rev3-1-.. and Rev3-2-... you can run in the windows mode of the Rev3 using a screen/keyboard/mouse as an example of a PLC with an operator dashboard/interface to control the PLC with the switches and with the screen pushbutton.

The Rev3-3-MQTT is an MQTT version, not further used as we focus on OPC-UA, where the operator dashboard is combined with sending the PLC status to an MQTT broker. At that broker MQTT apps and monitoring programs as MQTT.fx can be used.

The python example programs on the Rev requires that there is no other program on the RevPi controlling the I/O at the same time, i.e. you should stop the running program from revpipycontrol.exe  

`
 $kill -HUP id-of-revpipy`

Rev3-4-server is the OPC server program that runs in your Rev3. It does not require a screen/keyboard/mouse, so it must
be started from the prompt or ssh connection, but you can also start it from within a windows environment.

Rev3-4-192-.. is the client in the smart-factory 192.168.0.0/24 network and run from your PC wired to the same 192-network.
Rev3-4-10-.. with a client running on a PC in the 10.0.0.0/24 network and which access the firewall
at 10.0.0.254 op port 54840 to be dstnat-ed to 192.168.0.0/24 network to the OPC server at the Rev3 at 192.168.0.4:4840. The why and background of this is explained in the network directory. 

## Workshop participants Raspberry Pi's 

The example code for using the PI as an I/O device and OPC-UA server you find in the Pi directory.
For the OPC application you need two computers: a Pi as OPC-UA server and your PC as OPC-UA client. The code is with 10.0.0.4 as the demo server (the Pi with the Seeed Grove I/O) and in the same
10.0.0.0/24 network the client code runs on your own computer. 

As the participant Pi with the I/O are be numbered
10.0.0.11-16, you need to adapt in the source code in 21-grove.. or 21a-grove.. from the 10.0.0.4 to
your 10.0.0.1x IP numbers of your server/Seeed-grove Pi.

Finally, you can start on the 10.0.0.4 also Node-Red with pi@Pi-4:

`$ node-red-start`. 

It will start in a terminal box and once running you can open the webbrowser at 

`localhost:1880`

load the file: revpi.json and open an second webwindow using 

`localhost:1880/ui `

to see the dashboard (optionally after selecting at the localhost:1880  screen the deploy button). Stop node-red by opening an extra terminal window and type 

`$ node-red-stop.`

Egbert-Jan Sol
ejsol@dse.nl

*was TNO.nl*

