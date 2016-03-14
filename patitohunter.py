#!/usr/bin/python
__author__      = "Miguel A. Arroyo - @miguel_arroyo76"

import sys
import usb.core
import usb.util
import pyudev
import time
from pygame import mixer


def device_list(): # Return a list with connected devices
        list= []
	ids = []
        devices = usb.core.find(find_all=True)
        for dev in devices:
		ids.append(hex(dev.idVendor))
		ids.append(hex(dev.idProduct))
                list.append(ids)
		ids = []
        return list

def xor(list1, list2): # Return a list with the new device
    outputlist = []
    list3 = list1 + list2
    for i in range(0, len(list3)):
        if ((list3[i] not in list1) or (list3[i] not in list2)) and (list3[i] not in outputlist):
             outputlist[len(outputlist):] = [list3[i]]
    return outputlist

print "  _____        _    _  _           _    _                _              "
print " |  __ \      | |  (_)| |         | |  | |              | |             "
print " | |__) |__ _ | |_  _ | |_  ___   | |__| | _   _  _ __  | |_  ___  _ __ "
print " |  ___// _` || __|| || __|/ _ \  |  __  || | | || '_ \ | __|/ _ \| '__|"
print " | |   | (_| || |_ | || |_| (_) | | |  | || |_| || | | || |_|  __/| |   "
print " |_|    \__,_| \__||_| \__|\___/  |_|  |_| \__,_||_| |_| \__|\___||_|   "
print
print " 14th March 2016"
print " Version: 0.1"
print " By Miguel A. Arroyo - @miguel_arroyo76"

# Initializing lists
diff_list = []
first_list = device_list()

# Initializing boolean token
isBadUsb = False

context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='usb') #Filtering only for usb devices
monitor.start()

for device in iter(monitor.poll, None):
	action = device.action
	changed_list = device_list()
	diff_list = xor(changed_list,first_list)
	if action == "add":
		idV, idP = diff_list[0]
		dev = usb.core.find(idVendor=int(idV,16), idProduct=int(idP,16))
		interface = 0
		if dev.is_kernel_driver_active(interface) is True:
			print
			print "New USB device connected:"
        	        print "Vendor: ",idV
	                print "Product: ", idP
			# Detaching kernel driver
			dev.detach_kernel_driver(interface)
			# Claiming the device
			usb.util.claim_interface(dev, interface)
			for cfg in dev:
					print "Number of interfaces: ", cfg.bNumInterfaces
					intf = usb.util.find_descriptor(cfg, bInterfaceNumber=0)
					print "Interface Class: ", intf.bInterfaceClass
					if intf.bInterfaceClass == 3:
						print "Device Type: HID"
					print "Interface SubClass: ", intf.bInterfaceSubClass
					if intf.bInterfaceSubClass == 1:
						print "Protocol: Boot Protocol"
					if cfg.bNumInterfaces == 1 and intf.bInterfaceClass == 3 and intf.bInterfaceSubClass == 1:
						print "Atention! Probably a BadUsb"
						print "Device not mounted! Disconnect the device!"
						mixer.init()
						mixer.music.load('aud/duck.mp3')
						mixer.music.play()
					else:
						# Release the device
						usb.util.release_interface(dev, interface)
						# Reattach the device to the OS kernel
						dev.attach_kernel_driver(interface)


