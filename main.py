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

import config
import messages
import commands
import connection
import signals
import tabs

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


NIGIRI_VERSION = "0.0.1"


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

		# main loop
		while True:
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

	def quit(self):
		Signals.emit (self, "quit")

		self.ui.stop()

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
					# TODO
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
			switch_to_previous_tab(self)

		elif key == "ctrl n":
			switch_to_next_tab(self)

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



	def add_server(self, server):
		self.servers.append(server)

		Signals.connect(server, "remove",
			self.handle_server_remove)
		Signals.connect(server, "child_added",
			self.handle_channel_add)
		Signals.connect(server, "child_removed",
			self.handle_channel_remove)

		self.update_divider()

	def find_server(self, server_name):
		try:
			i = [n.name.lower() for n in self.servers].index(server_name.lower())
		except ValueError:
			return None
		else:
			return self.servers[i]

	def find_tab(self, tab_name):
		tablist = tabs.tree_to_list(self.servers)
		try:
			i = [n.name.lower() for n in tablist].index(tab_name.lower())
		except IndexError:
			return None
		else:
			return tablist[i]
		return None

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

	def handle_channel_add(self, server, channel):
		pass

	def handle_channel_remove(self, server, channel):
		if channel == self.current_tab:
			self.switch_to_next_tab()

	def switch_to_tab(self, tab):
		self.current_tab = tab

		if not tab:
			self.body.set_body(self.generic_output_walker)

		else:
			self.body.set_body(tab.output_walker)

		self.update_divider()

		Signals.emit(self, "tab_switched", tab)

	def switch_to_next_tab (main):
		tablist = tabs.tree_to_list(main.servers)

		try:
			current_index = tablist.index (main.current_world)
		except ValueError:
			return

		if (current_index + 1) >= len (tablist):
			current_index = 0
		else:
			current_index += 1

		main.switch_to_tab (tablist[current_index])

	def switch_to_previous_tab (main):
		tablist = tabs.tree_to_list(main.servers)
		try:
			current_index = tablist (main.current_world)
		except ValueError:
			return

		main.switch_to_tab (tablist[current_index - 1])


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
			temp = "%(nick)s@%(server)s:%(tab)"

			if self.current_tab:
				subdict = {
					"tab":str(self.current_tab),
					"nick":"",
					"server":""
				}

				if type(self.current_tab) == tabs.Server:
					subdict["nick"] = self.current_tab.get_nick()
					subdict["server"] = str(self.current_tab)
				else:
					subdict["nick"] = self.current_tab.parent.get_nick()
					subdict["server"] = str(self.current_tab.parent)

				markup.append(("divider", temp % subdict))

			else:
				markup.append(("divider", "-@-:-"))

		markup.append(("divider", "["))
		tablist_len = len(tablist)

		for i in range(tablist_len):
			tab = tablist[i]
			name = str(i+1)
			color = "divider"
			if tab.has_status("new_action"):
				color = "div_fg_green"

			if tab.has_status("new_message"):
				color = "div_fg_white"

			if tab.has_status("highlight_action"):
				color = "div_fg_yellow"

			if tab.has_status("highlight"):
				color = "div_fg_magenta"

			if i+1 != tablist_len:
				name += ","

			markup.append((color, name))

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

	signals.setup(main_window)

	messages.setup()

	main_window.main()
