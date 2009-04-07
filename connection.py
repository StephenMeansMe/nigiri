# coding: UTF-8
"""
Copyright (c) 2009 Marian Tietz
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE AUTHORS AND CONTRIBUTORS ``AS IS'' AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.
"""

import os

import dbus
from dbus.mainloop.glib import DBusGMainLoop

from signals import parse_from

dbus_loop = DBusGMainLoop()
bus_address = os.getenv("SUSHI_REMOTE_BUS_ADDRESS")
if bus_address:
	bus = dbus.bus.BusConnection(bus_address, mainloop=dbus_loop)
else:
	bus = dbus.SessionBus(mainloop=dbus_loop)

sushi = None
__connected = False

def connect():
	"""
		Connect to maki over DBus.
		Returns True if the connection attempt
		was succesful.
	"""
	global sushi

	proxy = None
	try:
		proxy = bus.get_object("de.ikkoku.sushi", "/de/ikkoku/sushi")
	except dbus.exceptions.DBusException, e:
		print e
		print "Is maki running?"

	if not proxy:
		return False

	sushi = dbus.Interface(proxy, "de.ikkoku.sushi")

	global __connected
	__connected = True

	return True

def disconnect():
	global sushi, __connected
	sushi = None
	__connected = False

def is_connected():
	"""
		Returns True if we are connected to maki.
	"""
	return __connected

