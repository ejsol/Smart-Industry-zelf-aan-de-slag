## Hardware configuration of Pi-11 till Pi-16

6 Pi's (we currently use Pi Model 3B+) with fixed IP nr 10.0.0.11 till 10.0.0.16

Grove Base Hat for Raspberry Pi [see Seeedstudio.com](https://wiki.seeedstudio.com/Grove_Base_Hat_for_Raspberry_Pi/)  

Grove high accuracy temperature sensor on I2C port

3 x Grove LED button on D5, D16 and D18 ports of the Base Hat (input button, output LED)

3 x Grove Relay on D22, D24 and D26 (outputs)

## Software configuration
Install the following Python3 libraries

pip3 install grove.py

pip3 install upm

sudo apt install python3-mraa python3-upm
    # you might need to move dist-packages in python3.4 to 3.7

pip3 install opcua

pip3 install opcua-client --user

pip3 install pyqtgraph

Then change in the directory of grove.py the files factory.py and mcp9808.py as described in Network../README grove multi..

You can run server (ocp.tcp://0.0.0.0:4840) on localhost
and then in terminal mode: $opcua-client on same host with connect to localhos. And if you want to run it from command prompt, make sure you converted with dos2unix the line with the shebang:

```
#!/usr/bin/python3
```
