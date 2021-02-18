# Configuration of Pi

- download Raspberry Pi Imager from www.raspberrypi.org/downloads and install a Raspberry Pi OS image on a microSD card 
- verify & finish imager and insert SD card into Pi
- hook up keyboard, mouse, display and opt. Ethernet and boot & initialize with welcome Pi

once Pi runs, go to Pi menu 

- Preferences 
	* 	Raspberry Pi Configuration 
		* 	on third tab active (check box) interfaces:
			* 			- ssh, VNC and I2C (and optional camera)

now run the following command in a terminal (command line)

```bash
sudo apt update
sudo apt upgrade

pip3 install opcua
```

now come the installation for the Seeed Studio grove.py software and related libraries. use

```bash
curl -sL https://github.com/Seeed-Studio/grove.py/raw/master/install.sh | sudo bash -s -
```
or by step by step: add first the repository:

```bash 
echo "deb https://seeed-studio.github.io/pi_repo/ stretch main" | sudo tee /etc/apt/sources.list.d/seeed.list
```
add public repository key

```bash
curl https://seeed-studio.github.io/pi_repo/public.key | sudo apt-key add -
```
install MRAA and UPM python3 libraries

```bash
sudo apt update
sudo apt install python3-mraa python3-upm
```

install library raspberry-gpio-python for RPi

```bash
sudo apt update
sudo apt install python3-rpi.gpio
```

install library rpi_ws281x for RPi

```bash
sudo pip3 install rpi_ws281x
```

install grove.py

```bash
sudo pip3 install grove.py
```

And finally the most complex part, the modification of the Grove library to accept multiple I2C temperature sensors. 
Seeed Grove has hard-coded I2C for only one I2C high accuracy temperature sensor, on I2C addr 0x18. However, the hardware itself can be modified for other addresses too by connection soldering pads.

In our example we modified one standard sensor with 0x18 into a second sensor on address 0x19 by connecting the pads
and, most complicated, but with Python you do get the library sources, modified three files for the grove.py. See details description in README grove multiple I2C.md file

You can avoid this and work with only one I2C high accuracy sensor (and a less accurate analoge sensor). In that case no library editing is necessary, you can skip it, but you need to adapt a little the example code. Either delete the second sensor and the line with the 0x19 addr or replace that line with the call to the analoge sensor
(see for the analoge sensor the Demo Pi-4 code, e.g. 1-Pi-4-Cli line 98)

Now you only need to clone the Python programs from github ejsol/Smart-Industry-zelf-aan-de-slag

```bash
git clone https://github.com/ejsol/Smart-Industry-zelf-aan-de-slag.git
```

and for easy use latter on copy the Pi files to the Desktop

```bash
cp ./Smart-Industry-zelf-aan-de-slag/Pi/*.* ./Desktop/.
```

click on the 0-grove-cli.py file and executive it in terminal mode

Check: If the two sensor values are identical and even if you warm one, both output increase, then the modification of the libraries went wrong. Check if there is a use of the home/pi/.local/lib/ instead of a /usr/local library files. (this is depending on the path you are using when starting python)