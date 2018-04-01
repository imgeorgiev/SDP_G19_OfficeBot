# Raspberry Pi files for OfficePal

## 1. Setup

#### 1. Install Raspbian

Go to the [Raspbian page](https://www.raspberrypi.org/downloads/raspbian/) and download Raspbian Stretch Lite. Then follow the installation guide and flash it on a SD card.

Note: min SD card size is 8GB.

#### 2. Enable SSH

Once flash is done you need to create an empty file called `ssh` into the boot partition of the SD card. This enables you to SSH into the rpi

#### 3. Connect to eduroam

Start editing networking file `**` and add

```
identitty:"unn@ed.ac.uk
password:"yourpassword"
esp=PEAP
phase1="peaplabel=0"
phase2="auth=MSCHAPV2"
priority=999
disabled=0
ssid="eduroam"
scan_ssid=0
mode=0
auth_alg=OPEN
proto=WPA RSN
pariwise=CCMP TKIP
key_mgmt=WPA-EAP
protective_key_caching=1
```


Then you will need to add it to an the automatic network configuration. Open file `/etc/network/interfaces.d` and add

```
auto lo
iface lo inet loopback
auto eth0
allow-hotplug eth0
iface eth0 inet manual
auto usb0
allow-hotplug usb0
iface usb0 inet manual
allow-hotplug wlan0
iface wlan0 inet manual
wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
```


#### 4. Set up connection to EV3
First you need to set up the networking settings on the EV3. On it, go to `Wireless and Networks/All Network Connections/Wired/IPv4` and set the settings to:
```
IP address: 169.254.21.44
Mask: 255.255.0.0
Gateway: 169.254.21.1
```

Note: We had issues with nested SSHing from Windows.

#### 5. Install necessary packages
```
sudo apt-get install python-pip3
sudo apt-get install python-pip
sudo pip3 install Flask pyserial apscheduler
sudo pip install pygame
```

Install [OpenCV](https://gist.github.com/willprice/c216fcbeba8d14ad1138)

#### 6. Enable remote connection
Follow guide on [Dataplicity](https://www.dataplicity.com/)


## 2. Controlling the setup

Connect to the RPi via the Ethernet cable. On Linux you must configure the local network from your machine to 'Shared with other computers'. Similar on Windows

Now you should be able to SSH into the RPi using:


`ssh pi@rspi.local` Password: `r0b0tpow3r`


From there you should be able to SSH into the EV3:


`ssh robot@ev3dev.local`
Password: `maker`


You can transfer files between machines using `scp` or simply downloading stuff from Github.


Alternatively, you can also connect to it through online.

Go to [Dataplicity](https://www.dataplicity.com/)
```
user: ignat.m.georgiev@gmail.com
pass: r0b0tpow3r
```

Note: you can't transfer files from there so best use GitHub for any file transfer

## 3. Communication between RPi and EV3
Achieved via TCP packets send between the two. RPi acting as a server and the EV3 acting as a client.

To achieve this we have used the [tcpcom libary](http://www.aplu.ch/home/apluhomex.jsp?site=164).

Comms packets:

Each package has a header and comma-seperated parameters: `CMD:L,50`. Commands include:
- CMD - Motor command -  RPi to EV3 - `CMD:50,50`. Paramters: speed left wheel (-100 to 100), speed right wheel.
- TRN - Turn command - RPi to EV3 - `TRN:90`. Paramters: degrees to turn.
- SPK - Speak command - RPi to EV3 - `SPK:retrospark`. Parameters: string to speak out.

First you have to start the parser on the EV3 which can be started using the `start_ev3.sh` script. Note - the EV3 must be in the same network as the RPi

Then simply import the `tcp_rpi.py` class into your code and use its functions. Should be straightforward, if not look into its code and `tcpcom_py3.py`.


## 4.Control directly via PS4 controller
Launch `python3 ~/SDP_G19_OfficeBot/rpi/tcp/tcp_rpi.py` with the joystick connected to the RPi.

