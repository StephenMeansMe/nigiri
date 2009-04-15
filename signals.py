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
import inspect

import config
import tabs

from messages import print_tab, print_error, \
	print_tab_notification, print_tab_error, \
	format_message

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

def maki_disconnected():
	for signal in signals:
		for handler in signals[signal]:
			signals[signal][handler].remove()

def maki_connected(sushi_interface):
	""" called by dbus connection handler.
		sushi is the dbus interface
	"""
	global sushi, signals

	maki_disconnected()

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
	for server in sushi.servers():
		stab = main_window.find_server(server)

		if stab:
			stab.set_connected(True)
			continue

		stab = tabs.Server(name = str(server))
		main_window.add_server(stab)

		sushi.nick(server, "")

		for channel in sushi.channels(server):
			ctab = main_window.find_tab(server, channel)

			if ctab:
				ctab.set_joined(True)
				sushi.topic(server, channel, "")
				continue

			ctab = tabs.Channel(name = channel,
				parent = stab)
			ctab.set_joined(True)
			sushi.topic(server, channel, "")
			sushi.names(server, channel)

		stab.set_connected(True)

	main_window.update_divider()

####################################################

def find_parent_tab(server, target):
	parent = main_window.find_server(server)
	if not parent:
		print_error("parent server '%s' for '%s' not found." % (
			server, target))
		return None
	return parent

def no_tab_error(msg):
	def dec(fun):
		def subdec(*args, **kwargs):
			parameters = inspect.getargspec(fun)[0]
			param_dict = {}

			for i in range (len(args[:len(parameters)])):
				param_dict[parameters[i]] = args[i]
			param_dict.update (kwargs)

			tab = fun(*args, **kwargs)
			if not tab:
				print_error(msg % param_dict)

			return tab
		return subdec
	return dec

@no_tab_error ("No tab found for %(target)s on %(server)s. (nick = %(nick)s)")
def find_target_tab(server, target, nick):
	""" server: current server,
		target: target of the action,
		nick: causes the action

		Return a query-tab if target is a user,
		return a channel-tab if target is a channel
	"""
	if not target[0] in sushi.support_chantypes(server):
		# we got a query here
		return find_query_tab(server, nick)

	else:
		return find_channel_tab(server, target)
	return None

@no_tab_error ("No tab for %(partner)s on %(server)s found.")
def find_query_tab(server, partner):
	tab = main_window.find_tab(server, partner)

	if tab:
		return tab

	parent = find_parent(server, partner)

	if not parent:
		return None

	tab = tabs.Query(name = partner, parent = parent)
	return tab

@no_tab_error ("No tab for channel %(channel)s on %(server)s found.")
def find_channel_tab(server, channel):
	tab = main_window.find_tab(server, channel)

	if tab:
		return tab

	parent = find_parent(server, target)

	if not parent:
		return None

	tab = tabs.Channel(name = target, parent = parent)
	return tab

def is_highlighted(server, message):
	words = config.get_list("chatting", "highlight_words")
	server_tab = main_window.find_server(server)

	if not server_tab:
		print_error("No server tab for server '%s'!" % (server))
		return False

	words.extend(server_tab.get_nick())
	words = [n.lower() for n in words if n]

	lower_message = message.lower()

	for word in words:
		try:
			lower_message.index(word)
		except ValueError:
			continue
		else:
			return True
	return False

def current_server_tab_print(server, message):
	""" for server related notifications.
		print the message to the current active tab
		if the tab belongs to the given server.
		If no tab of the given server is active, print
		it to the server tab.
	"""
	current_tab = main_window.current_tab

	if (not current_tab
		or (type(current_tab) == tabs.Server and current_tab.name != server)
		or (current_tab.parent.name != server)):
		# print it to the server tab
		tab = main_window.find_server(server)
		print_tab(tab, message)
	else:
		print_tab(current_tab, message)

# message signals

def sushi_action(time, server, sender, target, message):
	tab = find_target_tab(server, target, parse_from(sender)[0])

	if not tab:
		return

	type = "action"
	if is_highlighted(server, message):
		type = "highlight_action"

	msg = format_message(type, message, nick = parse_from(sender)[0])
	print_tab(tab, msg)

def sushi_message(time, server, sender, target, message):
	tab = find_target_tab(server, target, parse_from(sender)[0])

	if not tab:
		return

	mtype = "message"
	if is_highlighted(server, message):
		mtype = "highlight_message"

	nick = parse_from(sender)[0]

	if type(tab) == tabs.Channel:
		template = config.get("formats", "nick")
		nick = template % {
			"nick": nick,
			"prefix": sushi.user_channel_prefix(server, target, nick)}

	msg = format_message(mtype, message, nick = nick)
	print_tab(tab, msg)

def sushi_ctcp(time, server, sender, target, message):
	pass

def sushi_notice(time, server, sender, target, message):
	pass

# action signals


def sushi_invite(time, server, sender, channel, who):
	""" sender can be empty """
	# TODO: gettext

	if sender:
		sender_name = parse_from(sender)[0]
	else:
		sender_name = "Somebody"

	msg = "%(sender)s invited %(who)s to %(channel)s" % {
		"sender": sender_name,
		"channel": channel,
		"who": who}

	msg = format_message("status", msg)

	current_server_tab_print(server, msg)

def sushi_join(time, server, sender, channel):

	server_tab = main_window.find_server(server)

	if not server_tab:
		print_error("Missing server tab for '%s'." % (server))
		return

	tab = main_window.find_tab(server, channel)
	nick = parse_from(sender)[0]

	if nick == server_tab.get_nick():
		# we join
		if not tab:
			tab = tabs.Channel(name = channel, parent = server_tab)

		tab.set_joined(True)

		msg = "You joined %(channel)s." % {
			"channel": channel}
		msg = format_message("highlight_status", msg)
		print_tab(tab, msg)

	else:
		# somebody joined
		msg = "%(nick)s (%(host)s) joined %(channel)s." % {
			"nick": nick,
			"host": sender,
			"channel": channel
		}
		msg = format_message("status", msg)
		print_tab(tab, msg)

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

		msg = "You are now known as %(new_nick)s." % {
			"new_nick": new}

		current_server_tab_print(server, msg)

	else:
		# print status message in channel tab
		msg = "%(old_nick)s is now known as %(new_nick)s." % {
			"old_nick": old,
			"new_nick": new}

		current_server_tab_print(server, msg)

def sushi_mode(time, server, sender, target, mode, parameter):
	""" from can be empty, parameter can be empty """
	pass

def sushi_oper(time, server):
	pass

def sushi_part(time, server, sender, channel, message):
	""" message can be empty """
	tab = find_tab(server, channel)

	if not tab:
		print_error("No tab for channel '%s' on '%s'." % (channel, server))
		return

	if find_tab.parent.get_nick() == parse_from(sender)[0]:
		# we parted
		tab.set_joined(False)
		msg = "You left %(channel)s." % {
			"channel": channel}
		msg = format_message("highlight_status", msg)
		print_tab(tab, msg)

	else:
		msg = "%(nick)s has left %(channel)s." % {
			"nick": parse_from(sender)[0],
			"channel": channel}
		msg = format_message("status", msg)
		print_tab(tab, msg)

def sushi_quit(time, server, sender, message):
	""" message can be empty """
	server_tab = main_window.find_server(server)

	if not server_tab:
		print_error("No server tab for server '%s'." % (server))
		return

	server_tab.set_connected(False)
	current_server_tab_print("You have quit %s." % (server))

def sushi_topic(time, server, sender, channel, topic):
	""" sender can be empty """
	tab = main_window.find_tab(server, channel)

	if not tab:
		print_error("No tab '%s' on '%s' for topic setting." % (channel, server))
		return

	tab.set_topic(topic)

	if parse_from(sender)[0] == tab.parent.get_nick():
		mtype = "highlight_status"
		nick = "You"
	else:
		mtype = "status"
		nick = parse_from(sender)[0]

	if nick:
		msg = "%(nick)s changed the topic to '%(topic)s'." % {
			"nick": nick,
			"topic": topic}
		msg = format_message(mtype, msg)
		print_tab(tab, msg)

	if tab == main_window.current_tab:
		# update topic bar
		main_window.header.set_text(tab.get_topic())

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

		print_tab_notification(tab, "Connecting...")

	elif tab.connected:
		tab.set_connected(False)

		print_tab_notification(tab, "Reconnecting...")

	else:
		print_tab_notification(tab, "Connecting...")

def sushi_connected(time, server):
	tab = main_window.find_server(server)

	if not tab:
		tab = tabs.Server(name = server)
		main_window.add_server(tab)

	print_tab_notification(tab, "Connected.")
	tab.set_connected(True)

def sushi_away(time, server):
	pass

def sushi_back(time, server):
	pass

def sushi_away_message(time, server, nick, message):
	pass

def sushi_shutdown(time):
	pass


