#!/usr/bin/env python

import sys

try:
	import urwid.curses_display
	import urwid
except ImportError, e:
	print >> sys.stderr, "Failed to import urwid: %s" % (e)
	print >> sys.stderr, "Do you have urwid installed?"
	sys.exit(1)

from urwid import Signals, MetaSignals

try:
	import gobject
except ImportError:
	print >> sys.stderr, "You need python-gobject installed."
	sys.exit(1)
import re

import config
import messages
import commands
import connection
import signals
import tabs
from typecheck import types

import extends
from extends import *
from input_history import InputHistory

"""
 -------context-------
| --inner context---- |
|| HEADER            ||
||                   ||
|| BODY              ||
||                   ||
|| DIVIDER           ||
| ------------------- |
| FOOTER              |
 ---------------------

inner context = context.body
context.body.body = BODY
context.body.header = HEADER
context.body.footer = DIVIDER
context.footer = FOOTER

HEADER = Notice line (urwid.Text)
BODY = Extended ListBox
DIVIDER = Divider with information (urwid.Text)
FOOTER = Input line (Ext. Edit)
"""


NIGIRI_VERSION = "0.0.2"


class MainWindow(object):

	__metaclass__ = MetaSignals
	signals = ["quit","keypress","tab_switched"]

	_palette = [
			('divider','black','dark cyan', 'standout'),
			('text','light gray', 'black'),
			('bold_text', 'light gray', 'black', 'bold'),
			("body", "text"),
			("footer", "text"),
			("header", "text"),

			("div_fg_red", "dark red", "dark cyan"),
			("div_fg_blue", "dark blue", "dark cyan"),
			("div_fg_green", "dark green", "dark cyan"),
			("div_fg_yellow", "yellow", "dark cyan"),
			("div_fg_magenta", "dark magenta", "dark cyan"),
			("div_fg_white", "white", "dark cyan"),
			("div_fg_black", "black", "dark cyan"),
		]

	def __init__(self):
		# current active world
		self.current_tab = None
		self.servers = []
		self.shortcut_pattern = re.compile(config.get(
			"nigiri", "shortcut_pattern"))

	def main(self):

		self.ui = urwid.curses_display.Screen ()
		self.ui.register_palette (self._palette)
		self.ui.run_wrapper (self.run)

	def run(self):
		size = self.ui.get_cols_rows ()

		self.setup_context()

		self.update_divider()

		self.generic_input_history = InputHistory(
				text_callback = self.footer.get_edit_text)

		# urwid main loop
		def urwid_main_loop (self, size):
			self.draw_screen (size)

			try:
				keys = self.ui.get_input ()
			except KeyboardInterrupt:
				self.quit()

			for k in keys:
				if k == "window resize":
					size = self.ui.get_cols_rows()
					self.keypress (size, k)
					continue

				else:
					self.keypress (size, k)
			return True

		gobject.idle_add(urwid_main_loop, self, size)

		self.gmainloop = gobject.MainLoop()
		self.gmainloop.run()

	def quit(self):
		Signals.emit (self, "quit")

		self.ui.stop()

		self.gmainloop.quit()

		config.write_config_file ()

		sys.exit(0)

	def setup_context(self):
		""" setup the widgets to display """

		# create widgets
		self.header = urwid.Text("nigiri version %s" % NIGIRI_VERSION)
		self.footer = extends.Edit.ExtendedEdit("> ")
		self.divider = urwid.Text("Initializing.")

		self.generic_output_walker = urwid.SimpleListWalker([])
		self.body = extends.ListBox.ExtendedListBox(self.generic_output_walker)

		# setup attributes
		self.header = urwid.AttrWrap (self.header, "divider")
		self.footer = urwid.AttrWrap (self.footer, "footer")
		self.divider = urwid.AttrWrap (self.divider, "divider")
		self.body = urwid.AttrWrap (self.body, "body")

		# apply config values
		if not config.get_bool ("nigiri", "wrap_input"):
			self.footer.set_wrap_mode ("clip")
		else:
			self.footer.set_wrap_mode ("space")

		self.context = urwid.Frame (self.body, header = self.header,
				footer = self.divider)
		self.context = urwid.Frame (self.context, footer = self.footer)

		self.context.set_focus ("footer")

	def keypress(self, size, key):
		Signals.emit (self, "keypress", size, key)

		if key in ("page up","page down"):
			self.body.keypress (size, key)

		elif key == "enter":
			# Parse data or (if parse failed)
			# send it to the current world
			input = self.footer.get_edit_text()

			self.footer.set_edit_text(" "*len(input))
			self.footer.set_edit_text("")

			if not commands.parse (self, input):
				# no parsable command, sending RAW
				if self.current_tab:
					# TODO:  send!
					# TODO:: also, check if joined and connected
					# TODO:: and stuff...
					pass

			if self.current_tab:
				history = self.current_tab.input_history
			else:
				history = self.generic_input_history

			history.add_entry (input)
			history.reset()

		elif key == "up":
			history = self.generic_input_history

			if self.current_tab:
				history = self.current_tab.input_history

			prev = history.get_previous()

			if prev == None:
				return

			self.footer.edit_pos = None
			self.footer.set_edit_text (prev)
			self.footer.set_edit_pos (len(prev))

		elif key == "down":
			history = self.generic_input_history

			if self.current_tab:
				history = self.current_tab.input_history

			next = history.get_next()

			if next == None:
				return

			self.footer.set_edit_text (next)
			self.footer.set_edit_pos (len(next))

		elif key == "ctrl p":
			self.switch_to_previous_tab()

		elif key == "ctrl n":
			self.switch_to_next_tab()

		elif self.shortcut_pattern.match(key):
			self.switch_to_tabid(int(key[-1]))

		elif key == "ctrl u":
			# clear the edit line
			self.footer.set_edit_text ("")
			self.footer.set_edit_pos (0)

		elif key == "ctrl w":
			# remove the text from cursor
			# position to previous space

			def ctrlw(et, ep):
				i = et[:ep].rfind(" ")
				if i == -1:
					et = et[ep:]
				else:
					et = et[:i+1] + et[ep:]
				return et

			# FIXME: fix position setting
			new = ctrlw(
				self.footer.get_edit_text(),
				self.footer.edit_pos)
			self.footer.set_edit_text(new)

		elif key == "ctrl l":
			# refresh the whole screen
			self.context._invalidate()
			self.draw_screen (size)

		else:
			self.context.keypress (size, key)




	def find_server(self, server_name):
		try:
			i = [n.name.lower() for n in self.servers].index(server_name.lower())
		except ValueError:
			return None
		else:
			return self.servers[i]

	def find_tab(self, parent_name, child_name = ""):
		try:
			i = [n.name.lower() for n in self.servers].index(parent_name.lower())
		except ValueError:
			return None
		else:
			if not child_name:
				return self.servers[i]
			else:
				try:
					j = [n.name.lower() for n in self.servers[i].children].index(child_name.lower())
				except ValueError:
					return None
				else:
					return self.servers[i].children[j]
		return None

	def add_server(self, server_tab):
		self.servers.append(server_tab)

		Signals.connect(server_tab, "remove",
			self.handle_server_remove)
		Signals.connect(server_tab, "child_added",
			self.handle_channel_add)
		Signals.connect(server_tab, "child_removed",
			self.handle_channel_remove)

		server_tab.input_history = InputHistory(
			text_callback = self.footer.get_edit_text)

		self.update_divider()

	def remove_server(self, server):
		try:
			i = self.servers.index(server)
		except ValueError:
			return
		else:
			del self.servers[i]
			self.update_divider()

	def handle_server_remove(self, server):
		self.remove_server(server)

	def handle_channel_add(self, server_tab, channel_tab):
		channel_tab.input_history = InputHistory(
			text_callback = self.footer.get_edit_text)
		self.update_divider()

	def handle_channel_remove(self, server_tab, channel_tab):
		if channel == self.current_tab:
			self.switch_to_next_tab()
		self.update_divider()

	def handle_maki_disconnect(self):
		pass

	@types(id = int)
	def switch_to_tabid(self, id):
		""" this is not for use with indexes! """
		tablist = tabs.tree_to_list(self.servers)
		if not config.get_bool("nigiri","server_shortcuts"):
			tablist = [n for n in tablist if type(n) != tabs.Server]
		try:
			tab = tablist[id-1]
		except IndexError:
			return
		self.switch_to_tab(tab)

	def switch_to_tab(self, tab):
		self.current_tab = tab

		if not tab:
			self.body.set_body(self.generic_output_walker)

		else:
			self.body.set_body(tab.output_walker)

		tab.reset_status()
		self.update_divider()

		Signals.emit(self, "tab_switched", tab)

	def switch_to_next_tab (self):
		tablist = tabs.tree_to_list(self.servers)

		try:
			current_index = tablist.index (self.current_tab)
		except ValueError:
			if tablist:
				self.switch_to_tab(tablist[0])
			return

		if (current_index + 1) >= len (tablist):
			current_index = 0
		else:
			current_index += 1

		self.switch_to_tab (tablist[current_index])

	def switch_to_previous_tab (self):
		tablist = tabs.tree_to_list(self.servers)
		try:
			current_index = tablist.index(self.current_tab)
		except ValueError:
			if tablist:
				self.switch_to_tab(tablist[0])
			return

		self.switch_to_tab (tablist[current_index - 1])


	# TODO:  update_divider without color usage
	# TODO:: for people who can't see colors

	def nc_update_divider(self):
		pass

	def update_divider(self):
		"""
		0: [maki] green or red highlighted
		1: "Not connected." or tab id
		if no connection: abort here.
		2: tab name
		3: tab list with highlights
		"""
		markup = []
		tablist = tabs.tree_to_list(self.servers)

		try:
			tabid = tablist.index(self.current_tab)
		except ValueError:
			tabid = -1

		# [maki]
		markup.append(("divider", "["))
		if connection.is_connected():
			markup.append(("div_fg_blue","maki"))
		else:
			markup.append(("div_fg_red","maki"))
		markup.append(("divider", "] "))

		if not self.servers:
			markup.append(("divider", "Not connected to any server."))
			self.divider.set_text(markup)
			return

		else:
			# add <nick>@<server>:<current tab>
			temp = "%(nick)s@%(server)s:%(tab)s (%(id)s) "

			if self.current_tab:
				subdict = {
					"tab":str(self.current_tab),
					"nick":"",
					"server":"",
					"id":""
				}

				if type(self.current_tab) == tabs.Server:
					subdict["nick"] = self.current_tab.get_nick() or "-"
					subdict["server"] = str(self.current_tab)
				else:
					subdict["nick"] = self.current_tab.get_parent()\
						.get_nick() or "-"
					subdict["server"] = str(self.current_tab.get_parent())

				subdict["id"] = str(tabid+1)

				markup.append(("divider", temp % subdict))

			else:
				markup.append(("divider", "-@-:-"))

		# display tabnumbers which are active
		markup.append(("divider", "["))
		active_tabs = [tab for tab in tablist if tab.status and tab != self.current_tab]
		active_tabs_len = len(active_tabs)

		for i in range(active_tabs_len):

			tab = active_tabs[i]
			try:
				name = str(tablist.index(tab)+1)
			except ValueError:
				name = "UNAVAIL"
			color = "divider"

			if tab.has_status("action"):
				color = "div_fg_green"

			if tab.has_status("message"):
				color = "div_fg_white"

			if tab.has_status("highlight_action"):
				color = "div_fg_yellow"

			if tab.has_status("highlight"):
				color = "div_fg_magenta"


			markup.append((color, name))

			if i+1 != active_tabs_len:
				markup.append(("divider", ","))

		markup.append(("divider", "]"))

		self.divider.set_text(markup)

	def print_text(self, text):
		"""
		print the given text in the _current_ window
		"""

		if not text or type(text) != str:
			raise TypeError, "text must be of type str"

		if self.current_tab:
			walker = self.current_tab.output_walker

		else:
			walker = self.generic_output_walker

		if text[-1] == "\n":
			text = text[:-1]

		walker.append (urwid.Text (text))

		self.body.scroll_to_bottom (self.ui.get_cols_rows())

	def draw_screen(self, size):
		canvas = self.context.render (size, focus=True)
		self.ui.draw_screen (size, canvas)

if __name__ == "__main__":
	global main_window

	config.setup()

	# TODO: setup locale stuff

	main_window = MainWindow()

	connection.setup([signals.maki_connected],
		[main_window.handle_maki_disconnect])

	signals.setup(main_window)

	messages.setup()

	main_window.main()
