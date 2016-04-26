#!/usr/bin/python
__author__      = "Miguel A. Arroyo - @miguel_arroyo76"
__version__		= "0.1"
__banner__ 		= """
  _____        _    _  _           _    _                _              
 |  __ \      | |  (_)| |         | |  | |              | |             
 | |__) |__ _ | |_  _ | |_  ___   | |__| | _   _  _ __  | |_  ___  _ __ 
 |  ___// _` || __|| || __|/ _ \  |  __  || | | || '_ \ | __|/ _ \| '__|
 | |   | (_| || |_ | || |_| (_) | | |  | || |_| || | | || |_|  __/| |   
 |_|    \__,_| \__||_| \__|\___/  |_|  |_| \__,_||_| |_| \__|\___||_|   

 14th March 2016
"""
__credit__		= __banner__ + " Version: " + __version__ + "\n By " + __author__

import sys
import usb.core
import usb.util
import pyudev
from pygame import mixer

def get_connected_devices(): # Return a list with connected devices
    return [(hex(device.idVendor), hex(device.idProduct)) for device in usb.core.find(find_all=True)]

def play_audio():
	mixer.init()
	mixer.music.load('audio/duck.mp3')
	mixer.music.play()

def check_for_badusb(cfg, intf, dev, interface):
	if cfg.bNumInterfaces == 1 and intf.bInterfaceClass == 3 and intf.bInterfaceSubClass == 1:
		print "Atention! Probably a BadUsb"
		print "Device not mounted! Disconnect the device!"
		play_audio()
	else:
		usb.util.release_interface(dev, interface) # Release the device
		dev.attach_kernel_driver(interface) # Reattach the device to the OS Kernel

def analyse_configurations(dev, interface):
	for cfg in dev:
		print "Number of interfaces: ", cfg.bNumInterfaces
		intf = usb.util.find_descriptor(cfg, bInterfaceNumber=0)
		print "Interface Class: ", intf.bInterfaceClass
		if intf.bInterfaceClass == 3:
			print "Device Type: HID"
		print "Interface SubClass: ", intf.bInterfaceSubClass
		if intf.bInterfaceSubClass == 1:
			print "Protocol: Boot Protocol"
		check_for_badusb(cfg, intf, dev, interface)

def inspect_added_usb(initial_devices):
	idV, idP = list(set(get_connected_devices()) - set(initial_devices))[0]
	dev = usb.core.find(idVendor=int(idV, 16), idProduct=int(idP, 16))
	interface = 0
	if dev.is_kernel_driver_active(interface) is True:
		print
		print "New USB device connected:"
		print "Vendor: ", idV
		print "Product: ", idP
		dev.detach_kernel_driver(interface) # Detaching Kernel driver
		usb.util.claim_interface(dev, interface) # Claiming the device
		analyse_configurations(dev, interface)				

def main():
	initial_devices = get_connected_devices()

	monitor = pyudev.Monitor.from_netlink(pyudev.Context())
	monitor.filter_by(subsystem='usb') #Filtering only for usb devices
	monitor.start()

	for usb in iter(monitor.poll, None):
		if usb.action == "add":
			inspect_added_usb(initial_devices)	

if __name__ == '__main__':
	print __credit__
	main()