# Firewall setting using a Mikrotik router

## 10-subnet (the engineering/office network)

The network consists of a smart-engineering router, a Mikrotik hAP, with the 10.0.0.0/24 network using the following addresses:

* 10.0.0.1 hAP router (during the session the WAN port ether1 is not connected to Internet)
* 10.0.0.2 RevPi core 1
* 10.0.0.3   reserved for RevPi core 3 (this RevPi core 3 is located at 192.168.0.3)
* 10.0.0.4 reserved for Pi-4 (demo Pi with 3 sensors)
* 10.0.0.10 Pi-10 configuration Pi
* 10.0.0.11-16 participants Pi's Pi-11 till Pi-16
* 10.0.0.20-100 DHCP
* 10.0.0.254 WAN port of router of the 192.168.0.0/24 smart-factory network, hEX router port 1 (ether1)

The hAP router uses the standard Mikrotik router setting (firewall, etc,) with both the 2.4Ghz and the 5Ghz Wi-Fi 1-5
activated to communicate with the wireless Pi-11 to Pi-16. Next to Wi-Fi it has 1 WAN and 4 Giga Ethernet ports.

Note: in setting up a workshop network, start this hAP router before the Pi-11 to Pi-16.

## 192-subnet (the shielded subnet with equipment/production line)

The 192.168.0.0/24 network smart-factory is shielded by a tightly locked-down router, a Mikrotik hEX router
with no wifi, only 4 Giga Ethernet ports (ether2-ether5) and the following configuration:

* 192.168.0.1 hEX router (no Wi-Fi)
* 192.168.0.3 RevPi core 3 (Rev3)
* 192.168.0.4 Pi-4
* 192.168.0.20-100 DHCP

The hEX router (RouterOS 6.45.3 model RB750Gr3)is connects on its WAN port (ether1) to the 10-net on fixed IP 10.0.0.254. It firewall rule set is replaced by the following setting
(copy text and enter it as script in the Mikrotik router terminal interface)

~~~
/ip firewall filter
add action=drop chain=input comment="drop invalid to firewall router at 192.168.0.1/24" connection-state=invalid
add action=accept chain=input comment="allow established connections to firewall router " connection-state=established
add action=accept chain=input comment="allow connection to firewall router from local network \
  (ether2-5 as ether1 is WAN)" in-interface=!ether1 src-address=192.168.0.0/24
add action=drop chain=input comment="drop all to firewall router not coming from LAN (also no icmp)" in-interface=ether1

add action=drop chain=forward comment="defconf: drop invalid" connection-state=invalid
add action=accept chain=forward comment="accept established and related" connection-state=established,related
add action=drop chain=forward comment="defconf:  drop all from WAN not DSTNATed" connection-nat-state=!dstnat \
    connection-state=new in-interface-list=WAN
add action=drop chain=forward comment="drop everything else " disabled=yes

/ip firewall nat
add action=masquerade chain=srcnat comment="defconf: masquerade" disabled=yes ipsec-policy=out,none out-interface-list=WAN
add action=dst-nat chain=dstnat dst-address=10.0.0.254 dst-port=54843 log=yes protocol=tcp to-addresses=192.168.0.3 to-ports=4840
add action=dst-nat chain=dstnat dst-address=10.0.0.254 dst-port=54844 log=yes protocol=tcp to-addresses=192.168.0.4 to-ports=4840

/ip firewall service-port
set ftp disabled=yes
set irc disabled=yes
set h323 disabled=yes
set sip disabled=yes
~~~

Note the line with the dst-nat (destination network address translation). If a packet arrives at 10.0.0.254 on port 54844 it is translated to address 192.168.0.4 port 4840. Port 4840 is the standard port for the OPC-UA protocol. This number is just chosen ourselves along the thinking that is should be above 50000 and have a relation to 192.168.0.4 as fixed number (therefore we said to ourselves that 50000 + 4840 + 4 would be 54844.)
