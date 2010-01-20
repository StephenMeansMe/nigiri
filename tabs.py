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

import sys
from typecheck import types
from dbus import String, UInt64

import urwid
from urwid import MetaSignals, SimpleListWalker, Text

import connection
import config

def tree_to_list(input_parents, target = None):

	l = []

	for parent in input_parents:

		if target and parent != target:
			continue

		l.append(parent)

		for child in parent.children:
			l.append(child)

	return l

def get_server(tab):
	if not tab:
		return None
	if type(tab) == Server:
		return tab
	else:
		parent = tab.parent
		if not parent:
			return None
		return tab.parent
	return None

class Tab(object):

	__metaclass__ = MetaSignals
	signals = ["child_added", "child_removed", "remove", "connected"]

	_valid_stati = [
		"informative",
		"actions", "actions_highlight","actions_own",
		"messages","messages_highlight","messages_own"]

	def __repr__(self):
		return "<tab: %s:%s:%s>" % (
			type(self).__name__, self._parent, self.name)

	def __str__(self):
		return self.name

	# Properties

	@types(switch = bool)
	def set_connected(self, switch):
		self._connected = switch

		for child in self.children:
			child.set_connected(switch)

		urwid.emit_signal(self, "connected", switch)

	connected = property(lambda x: x._connected, set_connected)

	def set_input_text(self, text):
		self._input_text = text

	input_text = property(lambda x: x._input_text, set_input_text)

	# Methods

	@types(name = (String, str, unicode))
	def __init__(self, name):
		self.name = name

		self._connected = False
		self._parent = None

		self.status = {}
		self.children = []
		self.input_history = None
		self.output_walker = SimpleListWalker([])
		self.input_text = ""

		self.read_line_index = -1

	def set_readline(self):
		if self.read_line_index != -1:
			try:
				del self.output_walker[self.read_line_index]
			except IndexError:
				pass

		line = Text("-"*30)
		line.set_align_mode ("center")
		self.output_walker.append(line)
		self.read_line_index = len(self.output_walker)-1

	def child_added(self, child):
		urwid.emit_signal(self, "child_added", self, child)
		child.set_connected(self.connected)
		self.children.append(child)

	def child_removed(self, child):
		urwid.emit_signal(self, "child_removed", self, child)
		try:
			i = self.children.index(child)
		except ValueError:
			pass
		else:
			del self.children[i]

	def set_parent(self, parent):
		if parent in self.children:
			print "Loop detected in '%s'.set_parent(%s)" % (
				self, parent)
			return

		try:
			self._parent.child_removed(self)
		except AttributeError:
			pass

		self._parent = parent

		try:
			self._parent.child_added(self)
		except AttributeError:
			pass

	parent = property(lambda x: x._parent, set_parent)

	def remove(self):
		""" emit remove signals """
		for child in self.children:
			child.remove()
			self.child_removed(child)
		urwid.emit_signal(self, "remove")
		self.set_parent(None)

	@types(name = str)
	def add_status(self, name):
		if name in self._valid_stati:
			self.status[name] = True

	@types(status = str)
	def has_status(self, status):
		return self.status.has_key(status)

	@types(name = str)
	def remove_status(self, name):
		try:
			del self.status[name]
		except KeyError:
			pass

	def reset_status(self):
		self.status = {}

	def print_last_log(self, lines=0):
		"""	Fetch the given amount of lines of history for
			the channel on the given server and print it to the
			channel's textview.
		"""
		lines = UInt64(lines or config.get(
			"chatting",
			"last_log_lines",
			"0"))

		if type(self) == Server:
			server = self.name
			channel = ""
		else:
			server = self.parent.name
			channel = self.name

		for line in connection.sushi.log(server, channel, lines):
			self.output_walker.append(Text(unicode(line)))

class Server(Tab):

	def __init__(self, name):
		Tab.__init__(self, name)

		self._nick = None
		self._away = ""

	@types(nick = (str,String))
	def set_nick(self, nick):
		self._nick = nick

	def get_nick(self):
		return self._nick

	@types(msg = str)
	def set_away(self, msg):
		self._away = msg

class NickList(dict):

	def __init__(self):
		dict.__init__(self)

	@types(nick = (str, unicode, String))
	def add_nick(self, nick):
		# TODO:  would be nice to have
		# TODO:: the hostmask as value but names()
		# TODO:: does not support this yet
		self[unicode(nick)] = 1

	@types(nick = (str, unicode, String))
	def get_hostmask(self, nick):
		return self[unicode(nick)]

	@types(old = (str, unicode, String),
		new = (str, unicode, String))
	def rename_nick(self, old, new):
		u_old = unicode(old)
		self[unicode(new)] = self[u_old]
		del self[u_old]

	@types(nick = (str, unicode, String))
	def remove_nick(self, nick):
		del self[unicode(nick)]

	@types(nick = (str, unicode, String))
	def has_nick(self, nick):
		return self.has_key(unicode(nick))

class Channel(Tab):

	@types(name = (String,str))
	def __init__(self, name, parent = None):
		Tab.__init__(self, name)
		self.joined = False
		self.set_parent(parent)
		self._topic = ""
		self.nicklist = NickList()

	@types(switch = bool)
	def set_joined(self, switch):
		self.joined = switch

	@types(topic = (String, unicode, str))
	def set_topic(self, topic):
		self._topic = unicode(topic)

	def get_topic(self):
		return self._topic

class Query(Tab):

	def __init__(self, name, parent = None):
		Tab.__init__(self, name)
		self.set_parent(parent)
