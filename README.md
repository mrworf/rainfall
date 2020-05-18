# rainfall
A python based sprinkler system which uses any raspberry pi connected to a relay board of your choice to control the sprinkler valves.

# background

I was using 2 x EzFlower. EzFlower is an insteon based 8 channel relay. The logic for the sprinklers still
has to be implemented by you. A fun exercise to be sure (at best it uses an if/this/else/that flow).

But keyword in that above paragraph is "was". This week, one of my boxes died. After a lot of grumbling and
cussing about having to cough up another $120 to keep it running, I decided to review my options.

Using a standard rainbird like when we got the house seemed a no-go since they usually have too few zones or lack
sophistication when it comes to scheduling. Going all out for a modern wifi enabled solution with enough zones
(I need at least 11) would cost nearly $200.

Instead decided to go my own way. I had a Raspberry Pi 2B lying around, and I found that for $10 you could get a nice 8 channel
relay board. And given the amount of GPIOs on RPi, you can get between 16 or 24 zones without any extra work (each board requires
8 GPIOs).

# hardware

This means you can build a 24 channel network enabled sprinkler system for about $60.

All you need is:
- Raspberry Pi (Zero Wireless ~$20)
- Memory card (noname ~$10)
- 3 x ELEGOO 8 Channel DC 5V (~$10)

And there you go. This assumes you have a suitable 5v USB powersupply already (which most of you probably do)

# what does it do

![example of setup](https://github.com/mrworf/rainfall/blob/master/images/ux1.png?raw=true)

Bootstrap style UX for add/edit/remove of sprinkler stations with a simple programming interface.
All stations have the following options:
- Duration (minutes)
- Cycles (minimum 1 or it won't run)
- Days (which days, every, every other)
- Shift (to allow sprinklers to run on different days if they have the same schedule)

Next, you can select when on the day it should run the program, with one distinction.
As usual you can decide at which time it should start, but you can also choose to have it
run so it will finish by a certain time.

This means if you want to be sure all sprinklers are done by 4am, now you can. The system
may start the program at 1.35am to reach that goal (based on your schedules).

# installation

## Install Raspbian Buster Lite

- Go to [raspberrypi.org](https://www.raspberrypi.org/) and download their [latest image](https://downloads.raspberrypi.org/raspbian_lite_latest)
- Write the image onto your SD card using [Etcher](https://www.balena.io/etcher/)

## Setup your environment

- Boot the RPi using the image you just wrote to the SD Card
- Setup your network as needed (so you can run headless)
- Change the `pi` default password (`raspberry`) to something harder
- Update your OS
```
sudo apt update
sudo apt upgrade -y
```
- Install the needed software
```
sudo apt install git python3-gpiozero python3-flask python3-flask-httpauth
```
- You may want to install the SSH server as well to allow remote administration
```
sudo apt install openssh-server
```
- Open `/boot/config.txt` file with an editor as root
```
sudo nano -w /boot/config.txt
```
- Find `dtparam=audio=on` and add a hash in-front of it, like so: `#dtparam=audio=on`
- To enable usage of all the GPIOs, go to the end of the file and add the following
```
gpio=2-26=op,dh
```
- Save and exit (hint, CTRL-X then `y` and ENTER)

## Install the software

- Start by cloning the software from github.com. Make sure you're in the home directory first
```
cd
git clone https://github.com/mrworf/rainfall.git
```
Any question about making the connection is normal since this is the first time. Simply agree and the download will commence.
- Run the installer
```
cd rainfall
sudo ./install.sh
```
- Done! Time to power off and connect the hardware
```
sudo poweroff
```

# using

The service runs on port 7770 by default, so once your raspberry is running, point your web browser to the
address of the device like so:
http://my.device.address:7770/

