#!/usr/bin/bash
echo "Install needed packets"
sudo apt install libusb-1.0-0-dev python3-pip python3-venv
echo "Add UDEV-rules for UNI-T UT161D-multimeter"
sudo cp ./99-ut161d.rules /etc/udev/rules.d/99-ut161d.rules
echo "Update UDEV-rules"
sudo udevadm control --reload-rules
sudo udevadm trigger
