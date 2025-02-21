# sample code comment

The standard Seeed-studio grove.py library from http://wiki.seeedstudio.com/Grove-I2C\_High\_Accuracy\_Temperature_Sensor-MCP9808/ only allows one I2C sensor on address 0x18. To use multiple sensors several changes are needed.

```py
# using the multiple I2C high accuracy temperature sensors
# 000 = 0x18
# 001 = 0x19
# 010 = 0x1A
# 100 = 0x1C
...
#     temperature = Factory.getTemper("MCP9808-I2C")
```
this is the standard call, but adding more I2C high-acc temp sensors requires soldering them (see website above) and modification of the call to e.g.

```py 
#      temperature = Factory.getTemper("MCP9808-I2C", 0x18)
```

and modifying two files in the standard Seeed-Studio library modules Factory.getTemper & TemperMCP9808 using sudo nano (it are library files):

in /usr/local/lib/Python3.7/dist_packages/grove/factory/factory.py change getTemper from

```py
   def getTemper(self, typ, channel = None): 
```
   
to

```py
def getTemper(self, typ, channel = None, addr = 0x18):
 ...
       elif typ == "MCP9808-I2C":
             return TemperMCP9808(addr)
```

and in ../lib/Python3.7/site_package/grove/temperature/mcp9808.py change TemperMCP9808 from

```py
   class TemperMCP9808(Temper):       
```
into

```py   
       class TemperMCP9808(Temper)
     def __init__(self):                       def __init__(self, addr):
          self.mcp = MCP9808(I2C.MRAA_I2C)          self.mcp = MCP9808(I2C.MRAA_I2C, addr)
```

and the final upm.pyupm\_mcp9808.py is standard prepared for address selection but it might be needed to modify it too at /usr/lib/python3/dist_packages/upm/pyupm_mcp9808.py from

```py
 def __init__(self, bus, addr=0x18)
```
into 
 
```py
 def __init__(self, bus, addr)
```

in other words remove the fixed addr.


The third library files (factory.py, mcp9808.py and upm.pyupm\_mcp9808.py)  you need to edit with

```bash
cd /usr/local/lib/Python3.7/dist_packages/grove/factory/
sudo nano factory.py
```

do the two edits of addr as describe above around line 146 and 150

```bash
cd  /usr/local/lib/Python3.7/site_package/grove/temperature/
sudo nano mcp9808.py
```

do the two edits of addr as describe above  at line 41 and 42 and the delete of =0x18 at line 137

```bash
cd /usr/lib/python3/dist_packages/upm/
sudo nano pyupm_mcp9808.py
```
Note: it might be that the setting of PATH forces that Python starts in /home/pi/.local/lib/python3.7/..
instead of /usr/local/lib/python3.7...
In that case you need to modify the files in the .local directory. 

Sample code with comment:

```py
import time
import sys
from datetime import datetime
from grove.factory import Factory
from grove.temperature import Temper


def main():
    # t_ad is temperature (in Celsius) at I2C address 0x..
    t_ad18 = Factory.getTemper("MCP9808-I2C", 0x18)
    t_ad18.resolution(Temper.RES_1_16_CELSIUS)

    t_ad19 = Factory.getTemper("MCP9808-I2C", 0x19)
    t_ad19.resolution(Temper.RES_1_16_CELSIUS)
```