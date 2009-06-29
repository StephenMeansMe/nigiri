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

from types import NoneType
from typecheck import types

import signals
from signals import parse_from
from messages import print_error

dbus_loop = DBusGMainLoop()
required_version = (1, 1, 0)
bus_address = os.getenv("SUSHI_REMOTE_BUS_ADDRESS")

if bus_address:
	bus = dbus.connection.Connection(bus_address, mainloop=dbus_loop)
else:
	bus = dbus.SessionBus(mainloop=dbus_loop)

class SushiWrapper (object):

	@types (sushi_interface = (dbus.Interface, NoneType))
	def __init__(self, sushi_interface):
		self._set_interface(sushi_interface)

	@types (connected = bool)
	def _set_connected(self, connected):
		self._connected = connected

	@types (interface = (dbus.Interface, NoneType))
	def _set_interface(self, interface):
		self._set_connected(interface != None)
		self._sushi = interface

	def __getattr__(self, attr):
		def dummy(*args, **kwargs):
			dialog = InlineMessageDialog(_("tekka could not contact maki."),
				_("There's no connection to maki, so the recent "
				"action was not performed. Try to reconnect to "
				"maki to solve this problem."))
			dialog.connect("response", lambda w,i: w.destroy())
			gui_control.showInlineDialog(dialog)

		if attr[0] == "_" or attr == "connected":
			# return my attributes
			return object.__getattr__(self, attr)
		else:
			if not self._sushi:
				return dummy
			else:
				if attr in dir(self._sushi):
					# return local from Interface
					return eval("self._sushi.%s" % attr)
				else:
					# return dbus proxy method
					return self._sushi.__getattr__(attr)
		raise AttributeError(attr)

	connected = property(lambda s: s._connected, _set_connected)

sushi = SushiWrapper(None)

_shutdown_handler = None
_connect_callbacks = []
_disconnect_callbacks = []

@types(connect_callbacks = list, disconnect_callbacks = list)
def setup(connect_callbacks, disconnect_callbacks):
	""" set callbacks """
	global _connect_callbacks, _disconnect_callbacks
	_connect_callbacks = connect_callbacks
	_disconnect_callbacks = disconnect_callbacks

def connect():
	"""
		Connect to maki over DBus.
		Returns True if the connection attempt
		was succesful.
	"""
	global sushi, _shutdown_handler

	proxy = None
	try:
		proxy = bus.get_object("de.ikkoku.sushi", "/de/ikkoku/sushi")
	except dbus.exceptions.DBusException, e:
		print_error("Error while connecting to maki: %s" % (e))
		print_error("Is maki running?")

	if not proxy:
		return False

	sushi._set_interface(dbus.Interface(proxy, "de.ikkoku.sushi"))

	version = tuple([int(v) for v in sushi.version()])

	if not version or version < required_version:
		sushi._set_interface(None)
		return False

	for callback in _connect_callbacks:
		callback(sushi)

	_shutdown_handler = sushi.connect_to_signal (
		"shutdown", lambda time: disconnect())

	return True

def disconnect():
	global sushi, __connected, _shutdown_handler
	sushi._set_interface(None)

	for callback in _disconnect_callbacks:
		callback()

	_shutdown_handler.remove()

