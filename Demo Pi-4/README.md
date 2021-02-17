# Demo Pi

The Pi-4 used for demonstration has more sensors then the Pi's used in the training.
The Pi-11 till Pi-16 in the training have only two Groove I2C high accuracy temperature sensor. Whereas the Pi-4
has next to the 2 I2C high accuracy temp sensor (two digits accuracy) also a very simple temperature sensor (zero digit) and
an air quality sensor.

The Demo Pi software differentiates for the Pi software as it reports more values in OPC-server and shows more in the client version.

## Hardware configuration of Pi-4:

Pi Model 4B (2GB RAM)

Grove Base Hat for Raspberry Pi

Grove 2 I2C high accuracy temperature sensors (but also read Network & hard../README on multiple I2C )

Grove temperature sensor on port A2

Grove air quality sensor v1.3 on port A6

3 x Grove LED button on D5, D16 and D18 ports of the Base Hat (input button, output LED)

3 x Grove Relay on D22, D24 and D26 (outputs)


## Software 
1-....py and 2-....py are demos of the usage of the Grove sensors. 

The 1-....py program only works in terminal/command line mode, i.e. only the physicals button works, but not screen. Program 2-...py shows on the Raspberry windows the dashboard such that button physical and screen button works together.

The 3-....py program is the OPC-UA server with the Pi-4 connected on the shielded smart-factory 192.168.0.0/24 subnet at IP nr 192.168.0.4.

Program 4-....py runs the client on a PC in the same 192.168.0.0/24 subnet. 

Program 5-....py is to be run as the PC OPC client in the 10-net, outside the shielded smart-factory network.

## Firewall setting

Pi-4 must be on 192.168.0.0/24 smart-factory network at 192.168.0.4 wired and shielded by the router/firewall between the 10-net and the 192-subnet 
where the firewall dstnat (destination NAT) filter rules has to be hard programmed. 
The Pi-4 needs to have the IP nr 192.168.0.4 where OPC-UA client on the PC in the samen 192-subnet will be listening on port 4840 (part of the hard programmed dstnat rule)
and in demo 5 with program 5....py on a PC in the 10net smart-engineering addressing the WAN side of the router/firewall will be at e.g. 10.0.0.254, then the dstnat setting to access the Pi-4 on port 4840 is 10.0.0.254:54844 (5 + 4840 + 4)