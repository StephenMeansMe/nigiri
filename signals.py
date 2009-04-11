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

import time

import config
import tabs

from messages import print_tab, print_error, \
	print_tab_notification, print_tab_error

sushi = None
signals = {}

def format_message(type, msg, **fmt):
	template = config.get("formats", type)

	if not template:
		print_error("No format template for type '%s'." % (type))
		return

	if not fmt.has_key("datestring"):
		fmt["datestring"] = time.strftime(config.get("formats","datestring"))

	fmt["message"] = msg

	return template % fmt

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



	# message receiving
	connect_signal("action", sushi_action)
	connect_signal("message", sushi_message)
	connect_signal("ctcp", sushi_ctcp)
	connect_signal("notice", sushi_notice)

	# action signals
	connect_signal("invite", sushi_invite)
	connect_signal("join", sushi_join)
	connect_signal("kick", sushi_kick)
	connect_signal("nick", sushi_nick)
	connect_signal("mode", sushi_mode)
	connect_signal("oper", sushi_oper)
	connect_signal("part", sushi_part)
	connect_signal("quit", sushi_quit)
	connect_signal("topic", sushi_topic)

	# informative signals
	connect_signal("banlist", sushi_banlist)
	connect_signal("cannot_join", sushi_cannot_join)
	connect_signal("list", sushi_list)
	connect_signal("motd", sushi_motd)
	connect_signal("names", sushi_names)
	connect_signal("no_such", sushi_no_such)
	connect_signal("whois", sushi_whois)

	# status signals
	connect_signal("connect", sushi_connect_attempt)
	connect_signal("connected", sushi_connected)
	connect_signal("away", sushi_away)
	connect_signal("back", sushi_back)
	connect_signal("away_message", sushi_away_message)
	connect_signal("shutdown", sushi_shutdown)

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

# message signals

def sushi_action(time, server, sender, target, message):
	pass

def sushi_message(time, server, sender, target, message):
	tab = main_window.find_tab(server, target)
	if not tab:
		print_error("Missing tab for '%s':'%s'" % (
			server, target))
		return

	msg = format_message("message", message, nick = parse_from(sender)[0])
	print_tab(tab, msg)

def sushi_ctcp(time, server, sender, target, message):
	pass

def sushi_notice(time, server, sender, target, message):
	pass

# action signals


def sushi_invite(time, server, sender, channel, who):
	""" sender can be empty """
	pass

def sushi_join(time, server, sender, channel):
	pass

def sushi_kick(time, server, sender, channel, who, message):
	""" message can be empty """
	pass

def sushi_nick(time, server, old, new):
	""" old == "" => new == current nick """
	stab = main_window.find_server(server)

	if not stab:
		print_error("missing stab '%s'" % server)
		return

	if not old or old == stab.get_nick():
		stab.set_nick(new)
		if main_window.current_tab in tabs.tree_to_list([stab]):
			main_window.update_divider()

	else:
		# TODO
		pass

def sushi_mode(time, server, sender, target, mode, parameter):
	""" from can be empty, parameter can be empty """
	pass

def sushi_oper(time, server):
	pass

def sushi_part(time, server, sender, channel, message):
	""" message can be empty """
	pass

def sushi_quit(time, server, sender, message):
	""" message can be empty """
	pass

def sushi_topic(time, server, sender, channel, topic):
	""" sender can be empty """
	pass


# informative signals

def sushi_banlist(time, server, channel, mask, who, when):
	""" who can be empty (""), when can be empty (0).
		mask == "" and who == "" and when == -1 => EOL
	"""
	pass

def sushi_cannot_join(time, server, channel, reason):
	""" reason is str:
		l - channel is full
		i - channel is invite only
		b - you're banned
		k - channel has key set
	"""
	pass

def sushi_list(time, server, channel, users, topic):
	""" channel == "" and users == -1 and topic == "" => EOL """
	pass

def sushi_motd(time, server, message):
	""" message == "" => End OR no MOTD """
	pass

def sushi_names(time, server, channel, nicks, prefix):
	""" len(nicks) == 0 => EOL """
	pass

def sushi_no_such(time, server, target, type):
	""" type is str:
		n - nick/channel
		s - server
		c - channel
	"""
	pass

def sushi_whois(time, server, nick, message):
	""" message == "" => EOL """
	pass

# status signals

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

def sushi_away(time, server):
	pass

def sushi_back(time, server):
	pass

def sushi_away_message(time, server, nick, message):
	pass

def sushi_shutdown(time):
	pass


