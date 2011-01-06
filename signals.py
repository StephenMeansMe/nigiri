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
from gettext import gettext as _

import string # is_highlight
import inspect
import time
import urwid
import logging

import config
import tabs
import connection

import helper.markup
import helper.code

from connection import parse_from, sushi

from messages import print_tab, print_error, \
	format_message, print_tab_notification

signals = {}
_backup_signals = []

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

	urwid.connect_signal(connection.sushi, "connected", maki_connected)
	urwid.connect_signal(connection.sushi, "disconnected", maki_disconnected)

def maki_disconnected(sushi):
	global signals, _backup_signals

	for signal in signals:
		for handler in signals[signal]:
			signals[signal][handler].remove()

			_backup_signals.append((signal,handler))
	signals = {}

def _reconnect_signals():
	global _backup_signals

	for (signal, handler) in _backup_signals:
		connect_signal(signal, handler)
	_backup_signals = []

def maki_connected(sushi_interface):
	""" called by dbus connection handler.
		sushi is the dbus interface
	"""
	global _backup_signals

	if _backup_signals:
		# restore saved signal/handler pairs
		_reconnect_signals()

	else:
		# initially setup signals

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
		connect_signal("list", sushi_list)
		connect_signal("motd", sushi_motd)
		connect_signal("names", sushi_names)
		connect_signal("whois", sushi_whois)
		connect_signal("error", sushi_error)

		# status signals
		connect_signal("connect", sushi_connect_attempt)
		connect_signal("connected", sushi_connected)
		connect_signal("away_message", sushi_away_message)
		connect_signal("user_away", sushi_user_away)
		connect_signal("shutdown", sushi_shutdown)
		connect_signal("dcc_send", sushi_dcc_send)

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

			ctab.print_last_log()

			sushi.names(server, channel)

			topic = sushi.channel_topic(server, channel)

			sushi_topic(time.time(), server, "", channel, topic)

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
		return find_query_tab(server, nick, create = True)

	else:
		return find_channel_tab(server, target, create = False)
	return None

@no_tab_error ("No tab for %(partner)s on %(server)s found.")
def find_query_tab(server, partner, create = True):
	tab = main_window.find_tab(server, partner)

	if tab:
		return tab

	if not create:
		return None

	parent = find_parent_tab(server, partner)

	if not parent:
		return None

	tab = tabs.Query(name = partner, parent = parent)
	return tab

@no_tab_error ("No tab for channel %(channel)s on %(server)s found.")
def find_channel_tab(server, channel, create = False):
	tab = main_window.find_tab(server, channel)

	if tab:
		return tab

	if not create:
		return None

	parent = find_parent_tab(server, channel)

	if not parent:
		return None

	tab = tabs.Channel(name = channel, parent = parent)
	return tab

def is_highlighted (server, text):
	def has_highlight(text, needle):
		punctuation = string.punctuation + " \n\t"
		ln = len(needle)
		for line in text.split("\n"):
			line = line.lower()
			i = line.find(needle)
			if i >= 0:
				if (line[i-1:i] in punctuation
				and line[ln+i:ln+i+1] in punctuation):
					return True
		return False

	server_tab = main_window.find_server(server)
	highlightwords = config.get_list("chatting", "highlight_words", [])
	highlightwords.append(server_tab.get_nick())

	for word in highlightwords:
		if has_highlight(text, word):
			return True
	return False

def current_server_tab_print(server, message):
	""" server: basestring
		message: basestring | FormattedMessage

		for server related notifications.
		print the message to the current active tab
		if the tab belongs to the given server.
		If no tab of the given server is active, print
		it to the server tab.
	"""
	current_tab = main_window.current_tab

	if (not current_tab
		or (type(current_tab) == tabs.Server and current_tab.name != server)
		or (current_tab.parent and current_tab.parent.name != server)):
		# print it to the server tab
		tab = main_window.find_server(server)
		print_tab(tab, message)
	else:
		print_tab(current_tab, message)


def color_nick_markup_cb(msg,values=["nick"]):
	def get_nick_color(nick):
		colors = main_window._palette[14:14+8]
		i = sum([ord(n) for n in nick]) % len(colors)
		return colors[i][0]

	if msg.own:
		return msg._markup()
	else:
		for val in msg.values:
			# Escape all values
			msg.values[val] = msg.values[val].replace(
				"\\","\\\\").replace("'","\\'")

			# Build markup tuples around values
			# This substitutes every input value to the form
			#   '),('color','value'),('base_color',
			# and embraces the generated template like this
			#   [('base_color','unicode(msg)')]
			# the following form is achieved
			#   [('base_color','Text '),('color','value'),
			#   	('base_color','...')]
			# repr is used for escaping.
			if val in values:
				msg.values[val] = "'),(%s,%s),(%s,u'" % (
					repr(get_nick_color(msg.values[val])),
					repr(msg.values[val]),
					repr(msg.base_color))
		x = "[(%s,u'%s')]" % (repr(msg.base_color),unicode(msg))
		return eval(x)

# message signals

def sushi_action(time, server, sender, target, message):
	nick = parse_from(sender)[0]
	tab = find_target_tab(server, target, nick)

	if not tab:
		return

	msg = format_message("messages", "action",
		{"nick": nick,
		 "message": message},
		own = (tab.parent.get_nick() == nick),
		highlight = (nick != tab.parent.get_nick()) and is_highlighted(server, message))

	print_tab(tab, msg)


def sushi_message(time, server, sender, target, message):
	nick = parse_from(sender)[0]
	tab = find_target_tab(server, target, nick)

	if not tab:
		return

	msg = format_message("messages", "message",
		{"message": message,
		 "nick": nick,
		 "prefix": sushi.user_channel_prefix(server, target, nick)},
		own = (nick == tab.parent.get_nick()),
		highlight = (nick != tab.parent.get_nick())
					and is_highlighted(server, message))

	msg.markup_cb = color_nick_markup_cb

	print_tab(tab, msg)

def sushi_ctcp(time, server, sender, target, message):
	own_nick = main_window.find_server(server).get_nick()
	nick = parse_from(sender)[0]

	msg = format_message("messages", "ctcp",
		{"nick": nick,
		 "target": target,
		 "message": message},
		own = (nick == own_nick),
		highlight = is_highlighted(server, message))

	msg.markup_cb = color_nick_markup_cb

	if target[0] in sushi.support_chantypes(server):
		tab = find_target_tab(server, target)
		if not tab:
			current_server_tab_print(server, msg)
	else:
		current_server_tab_print(server, msg)

def sushi_notice(time, server, sender, target, message):
	own_nick = main_window.find_server(server).get_nick()
	nick = parse_from(sender)[0]

	msg = format_message("messages", "notice",
		{"nick": nick,
		 "target": target,
		 "message": message},
		own = (nick == own_nick),
		highlight = is_highlighted(server, message))

	msg.markup_cb = color_nick_markup_cb

	if target[0] in sushi.support_chantypes(server):
		tab = find_target_tab(server, target)
		if not tab:
			current_server_tab_print(server, msg)
	else:
		current_server_tab_print(server, msg)

# action signals

def sushi_invite(time, server, sender, channel, who):
	""" sender can be empty """
	sender_name = parse_from(sender)[0]

	msg = format_message("actions", "invite",
		{"nick": sender_name,
		 "who": who,
		 "channel": channel},
		own = (sender_name == main_window.find_server(server).get_nick()),
		highlight = (who == sender_name))

	msg.markup_cb = color_nick_markup_cb

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
		main_window.update_divider()

	else:
		# somebody joined
		tab.nicklist.add_nick(nick)

	msg = format_message("actions", "join",
		{"nick": nick,
   		 "host": sender,
		 "channel": channel},
		own = (nick == server_tab.get_nick()),
		highlight = False)

	msg.markup_cb = color_nick_markup_cb

	print_tab(tab, msg)


def sushi_kick(time, server, sender, channel, who, message):
	""" message can be empty """
	stab = main_window.find_server(server)

	if not stab:
		print_error("missing stab '%s'" % (server))
		return

	nick = parse_from(sender)[0]
	tab = main_window.find_tab(server, channel)

	if who == stab.get_nick():
		# we got kicked
		pass

	else:
		tab.nicklist.remove_nick(who)

	msg = format_message("actions", "kick",
		{"who": who,
		 "channel": channel,
		 "nick": nick,
		 "reason": message},
		own = (who == stab.get_nick()),
		highlight = (nick == tab.parent.get_nick()))
	msg.markup_cb = color_nick_markup_cb

	print_tab(tab, msg)

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

		msg = format_message("actions", "nick",
			{"nick": old,
			 "new_nick": new},
			own = True,
			highlight = False)

		current_server_tab_print(server, msg)

	else:
		# print status message in channel tab
		old = connection.parse_from(old)[0]
		new = connection.parse_from(new)[0]

		msg = format_message("actions", "nick",
			{"nick": old,
			 "new_nick": new},
			own = False,
			highlight = False)

		msg.markup_cb = color_nick_markup_cb
		msg.markup_cb_kwargs = {"values":["nick","new_nick"]}

		for tab in stab.children:
			if type(tab) == tabs.Channel and tab.nicklist.has_nick(old):
				tab.nicklist.rename_nick(old,new)
				print_tab(tab, msg)

def sushi_mode(time, server, sender, target, mode, param):
	""" sender can be empty, param can be empty """
	if sender == "":
		# mode listing
		msg = format_message("actions", "mode_list",
			{"target": target, "mode": mode},
			own = (target == main_window.find_server(server).get_nick()),
			highlight = False)
		current_server_tab_print(server, msg)

	else:
		nick = parse_from(sender)[0]
		msg = format_message("actions", "mode",
			{"nick": nick,
			 "mode": mode,
			 "param": param and " "+param or "",
			 "target": target},
			own = (nick == main_window.find_server(server).get_nick()),
			highlight = (target == main_window.find_server(server).get_nick()))
		msg.markup_cb = color_nick_markup_cb

		tab = main_window.find_tab(server, target)
		print_tab(tab, msg)

def sushi_oper(time, server):
	msg = format_message("actions", "oper",
		{"nick": main_window.find_server(server).get_nick()},
		own = True,
		highlight = False)
	current_server_tab_print(server, msg)

def sushi_part(time, server, sender, channel, message):
	""" message can be empty """
	tab = main_window.find_tab (server, channel)
	nick = parse_from(sender)[0]

	if not tab:
		# ignore this cause it could be this tab was
		# closed recently
		return

	if tab.parent.get_nick() == nick:
		# we parted
		tab.set_joined(False)
		main_window.update_divider()

	else:
		tab.nicklist.remove_nick(nick)

	msg = format_message("actions", "part",
		{"nick": nick,
		 "channel": channel,
		 "reason": message},
		own = (tab.parent.get_nick() == nick),
		highlight = False)
	msg.markup_cb = color_nick_markup_cb

	print_tab(tab, msg)

def sushi_quit(time, server, sender, message):
	""" message can be empty """
	server_tab = main_window.find_server(server)

	if not server_tab:
		print_error("No server tab for server '%s'." % (server))
		return

	nick = parse_from(sender)[0]

	msg = format_message("actions", "quit",
		{"nick": nick,
		 "reason": message},
		own = (nick == server_tab.get_nick()),
		highlight = False)
	msg.markup_cb = color_nick_markup_cb

	if nick == server_tab.get_nick():
		# we quit
		server_tab.set_connected(False)

		for child in server_tab.children:
			print_tab(child, msg)

	else:
		for tab in server_tab.children:
			if type(tab) == tabs.Channel and tab.nicklist.has_nick(nick):
				tab.nicklist.remove_nick(nick)
				print_tab(tab, msg)
			elif (type(tab) == tabs.Query
				and tab.name.lower() == nick.lower()):
				print_tab(tab, msg)

def sushi_topic(time, server, sender, channel, topic):
	""" sender can be empty """
	tab = main_window.find_tab(server, channel)

	if not tab:
		print_error("No tab '%s' on '%s' for topic setting." % (
			channel, server))
		return

	tab.set_topic(topic)
	nick = parse_from(sender)[0]

	if sender == "":
		template = "topic_anonymous"
	else:
		template = "topic"

	msg = format_message("actions", template,
		{"nick": nick,
		 "channel": channel,
		 "topic": topic},
		own = (tab.parent.get_nick() == nick),
		highlight = False)
	if nick:
		msg.markup_cb = color_nick_markup_cb

	print_tab(tab, msg)

	if tab == main_window.current_tab:
		# update topic bar
		main_window.header.set_text(tab.get_topic())

# informative signals

def sushi_banlist(time, server, channel, mask, who, when):
	""" who can be empty (""), when can be empty (0).
		mask == "" and who == "" and when == -1 => EOL
	"""
	self = helper.code.init_function_attrs(sushi_banlist, first_run=True)

	if "" in (mask,who) and when == -1:
		# EOBL
		self.first_run = True

		msg = format_message("informative", "banlist_end",
			{"channel": channel},
			own = False,
			highlight = False)

		print_tab(self.tab, msg)
	elif self.started:
		# Listing just started

		self.first_run = False

		self.tab = main_window.find_channel_tab(server,channel)

		if not self.tab:
			# SHOULD NOT HAPPEN (banlist only in active channels)
			return

		msg = format_message("informative", "banlist_begin",
			{"channel": channel},
			own = False,
			highlight = False)

		print_tab(self.tab, msg)
	else:
		# Banlist item

		msg = format_message("informative", "banlist_begin",
			{"who": who,
			 "mask": mask,
			 "when": when},
			own = False,
			highlight = False)

		print_tab(self.tab, msg)

def sushi_list(time, server, channel, users, topic):
	""" channel == "" and users == -1 and topic == "" => EOL """
	pass

def sushi_motd(time, server, message):
	""" message == "" => End OR no MOTD """
	if message == "":
		# fetch support data
		server_tab = main_window.find_server(server)
		server_tab.update()
	pass

def sushi_names(time, server, channel, nicks, prefixes, _call_count = {"n":0}):
	""" len(nicks) == 0 => EOL """
	# TODO: colorize

	tab = find_channel_tab(server, channel)

	if not tab:
		return

	if _call_count["n"] == 0:
		msg = format_message("informative", "names_begin",
			{"channel": channel})
		print_tab(tab, msg)

	if len(nicks) != 0:
		max_width = 7
		width = 0
		msg = ""
		for nick in nicks:
			tab.nicklist.add_nick(nick)

			prefix = prefixes[width]
			msg += prefix+nick+" "

			if (width+1) % max_width == 0 or (width+1) == len(nicks):
				msg = msg[:-1]
				msg = format_message("informative", "names_item",
					{"row": msg})
				print_tab(tab, msg)
				msg = ""

			width += 1

		_call_count["n"] += 1

	else:
		msg = format_message("informative", "names_end", {})
		print_tab(tab, msg)
		_call_count["n"] = 0

def sushi_whois(time, server, nick, message):
	""" message == "" => EOL """
	pass

def sushi_error(time, server, domain, reason, arguments):

	def noSuch(time, server, target, type):
		if type == "nick":
			# no such nick/channel
			pass
		elif type == "server":
			# no such server
			pass
		elif type == "channel":
			# no such channel
			pass

	def cannotJoin(time, server, channel, reason):
		""" The channel could not be joined.
			reason : { l (full), i (invite only), b (banned), k (key) }
		"""
		if reason == "full":
			# channel is full
			pass
		elif reason == "invite":
			# channel is invite only
			pass
		elif reason == "banned":
			# you're bannend
			pass
		elif reason == "key":
			# needs key
			pass

	if domain == "no_such":
		noSuch(time, server, arguments[0], reason)

	elif domain == "cannot_join":
		cannotJoin(time, server, arguments[0], reason)

	elif domain == "privilege":
		if reason == "channel_operator":
			# need op
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

def sushi_away_message(time, server, nick, message):
	pass

def sushi_user_away(time, server, from_str, away):
	pass

def sushi_shutdown(time):
	pass

def sushi_dcc_send(time, id, server, sender, filename,
				size, progress, speed, status):
	""" handle dcc incoming/outgoing """
	# setup function attributes
	self = helper.code.init_function_attrs(sushi_dcc_send, new_register={})

	# import dcc states
	from helper.dcc import s_incoming, s_running, s_new

	logging.debug("dcc_send: (%d,%s,%s,%s)" % (id, server, sender, filename))

	if ("" in (server, sender, filename)
	and 0 in (size, progress, speed, status)):
		# file transfer removed
		logging.debug("filetransfer %d removed." % (id))

	else:
		if status & s_incoming:
			if status & s_new:
				logging.debug("incoming filetransfer (%d): %s %s %s" % (id, server, sender, filename))

				msg = format_message("informative", "dcc_new_incoming",
						{"sender": sender,
						 "id": id,
						 "filename": filename,
   						 "size": size})

				if main_window.current_tab:
					print_tab(main_window.current_tab, msg)
				else:
					main_window.print_text(unicode(msg))

				self.new_register[id] = True

			elif status & s_running and status & s_incoming:
				if not self.new_register.has_key(id):
					# notify about auto accepted file transfer
					msg = format_message(
							"informative",
							"dcc_file_auto_accept",
							{"sender": sender,
							 "filename": filename,
							 "size": size})

					if main_window.current_tab:
						print_tab(main_window.current_tab, msg)
					else:
						main_window.print_text(unicode(msg))

					self.new_register[id] = True



