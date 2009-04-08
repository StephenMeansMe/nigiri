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

import tabs

from messages import print_tab, print_error, \
	print_tab_notification, print_tab_error

sushi = None
signals = {}

def parse_from (from_str):
	h = from_str.split("!", 2)

	if len(h) < 2:
		return (h[0],)

	t = h[1].split("@", 2)

	if len(t) < 2:
		return (h[0],)

	return (h[0], t[0], t[1])

def connect_signal (signal, handler):
	""" connect handler to signal """
	global signals
	if type(signal) != type(""):
		raise TypeError

	if not signals.has_key (signal):
	  	signals[signal] = {}

	if signals[signal].has_key(handler):
		# no doubles
		return

	signals[signal][handler] = sushi.connect_to_signal (signal, handler)

def disconnect_signal (signal, handler):
	""" disconnect handler from signal """
	global signals
	if type(signal) != type(""):
		raise TypeError

	try:
		ob = signals[signal][handler]
	except KeyError:
		return
	else:
		ob.remove()
		del signals[signal][handler]


def setup(mw):
	""" called by main, mw is the main_window """
	global main_window
	main_window = mw

def maki_connected(sushi_interface):
	""" called by dbus connection handler.
		sushi is the dbus interface
	"""
	global sushi, signals
	sushi = sushi_interface
	signals = {}

	connect_signal("connect", sushi_connect_attempt)
	connect_signal("connected", sushi_connected)

	connect_signal("nick", sushi_nick)

	connect_signal("message", sushi_message)

	setup_connected_servers()

def setup_connected_servers():
	main_window.servers = []

	for server in sushi.servers():
		stab = tabs.Server(name = str(server))
		main_window.add_server(stab)

		sushi.nick(server, "")

		for channel in sushi.channels(server):
			ctab = tabs.Channel(name = channel,
				parent = stab)

	main_window.update_divider()

####################################################

def sushi_connect_attempt(time, server):
	tab = main_window.find_server(server)

	if not tab:
		tab = tabs.Server(name = server)
		main_window.add_server(tab)

		messages.print_tab_notification(tab, "Connecting...")

	elif tab.get_connected():
		tab.set_connected(False)

		messages.print_tab_notification(tab, "Reconnecting...")

	else:
		messages.print_tab_notification(tab, "Connecting...")

def sushi_connected(time, server):
	pass


def sushi_nick(time, server, old, new):
	""" old == "" => new == current nick """
	stab = main_window.find_server(server)

	if not stab:
		print_error("missing stab '%s'" % server)
		return

	if not old or old == stab.get_nick():
		stab.set_nick(new)
		if main_window.current_tab in tree_to_list([stab]):
			main_window.update_divider()

	else:
		# TODO
		pass

def sushi_message(time, server, sender, target, message):
	tab = main_window.find_tab(server, target)
	if not tab:
		print_error("Missing tab for '%s':'%s'" % (
			server, target))
		return

	print_tab(tab, "<%s> %s" % (parse_from(sender)[0], message))
