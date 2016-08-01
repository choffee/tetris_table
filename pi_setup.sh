#!/bin/bash

# Setup a pi from scratch to run the game.
# Should be able to run this over and over.
#

grep "ARM" /proc/cpuinfo >/dev/null || (echo "no pi?" && exit 1)

add_line() {
    local file=$1
    local line=$2
    grep "^${line}" "${file}" >/dev/null || echo "${line}" >> "${file}"
}

echo "Installing packages"
apt-get install -y python3-smbus python3-spidev python3-dev i2c-tools python3-pygame scons swig

echo "Enabling spi bus"
# Is there a module also?
add_line /boot/config.txt "dtparam=spi=on"

echo "Enabling i2c bus"
# Automaticaly load the module
add_line /etc/modules "i2c-dev"
add_line /etc/modules "i2c-bmc2708"
# Now set the boot config to turn it on.
add_line /boot/config.txt "dtparam=i2c1=on"
add_line /boot/config.txt "dtparam=i2c_arm=on"

echo "Adding pi users to groups"
adduser pi i2c
adduser pi spi
adduser pi tty
#cp -n /lib/udev/rules.d/50-udev-default.rules /lib/udev/rules.d/50-udev-default.rules.orig
#sed -i 's/SUBSYSTEM=="tty", KERNEL=="tty\[0-9\]\*", GROUP="tty", MODE="0620"/SUBSYSTEM=="tty", KERNEL=="tty[0-9]*", GROUP="tty", MODE="0660"/' /lib/udev/rules.d/50-udev-default.rules

echo "Setting hostname"
echo tetristable >/etc/hostname
sed -i "s/127.0.1.1.*/127.0.1.1\ttetristable/g" /etc/hosts

sync

test -d Adafruit_Python_GPIO || git clone https://github.com/adafruit/Adafruit_Python_GPIO
cd Adafruit_Python_GPIO
python3 setup.py install
cd ../

test -d rpi_ws281x || git clone https://github.com/richardghirst/rpi_ws281x
cd rpi_ws281x
sed -i 's/\/tmp\/mail/\/dev/rpi-mail/;s/makedev(100/makedev(249/' mailbox.c
scons
cd python
python3 setup.py install
cd ../../

echo "You might want to reboot now :)"

