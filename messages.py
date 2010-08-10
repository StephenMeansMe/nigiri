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


"""
provide methods for warnings, notifications, debug and errors
"""

import sys
import urwid
import urwid.util
import time

import config
from typecheck import types
import tabs
import helper

main_window = None

def setup (mw):
	global main_window
	main_window = mw

def get_nick_color(nick):
	"""
	Returns a static color for the nick given.
	The returned color depends on the color list
	set in config module.
	"""
	#return colors[sum([ord(n) for n in nick])%len(colors)]
	pass

color_tab = {
	"30": "text_fg_black",
	"31": "text_fg_red",
	"32": "text_fg_green",
	"33": "text_fg_yellow",
	"34": "text_fg_blue",
	"35": "text_fg_magenta",
	"36": "text_fg_cyan",
	"37": "text_fg_white",

	"1": "bold_text",
	"0": "body" # normal
	}

def parse_markup(input):
	"""
	search in input for \e and translate the ansi color
	number to the urwid color string.
	Parses \e[xm as well as \e[x;y;zm
	"""
	markup = []

	split = input.split ("\033")

	if split[0]:
		markup.append (("body",split[0]))

	for sub in split[1:]:
		if not sub:
			continue

		color,text = sub.split ("m", 1)

		for subcolor in color.split (";"):
			subcolor = subcolor.lstrip ("[")

			try:
				attr = color_tab[subcolor]
			except KeyError:
				attr = "body"

		markup.append ((attr, text))

	return markup

class FormattedMessage(object):

	@property
	def markup_cb(self): return self._markup_cb
	@markup_cb.setter
	def markup_cb(self, cb): self._markup_cb = cb

	@types( category = basestring, template = basestring,
			values = dict, highlight = bool, own = bool )
	def __init__(self, category, template, values, base_color,
				 highlight = False, own = False):
		self.category = category
		self.template = template
		self.values = values
		self.highlight = highlight
		self.base_color = base_color
		self.own = own 	# we triggered that/we are meant by it

		self.markup_cb = None

	def __str__(self):
		try:
			return self.template % (self.values)
		except KeyError,e:
			return "TEMPLATE_MISSING_KEY(%s)" % (e)

	def markup(self):
		if self.markup_cb:
			return self.markup_cb(self)
		return unicode(self)


@types (mtype=basestring, template_id=basestring, values=dict)
def format_message(mtype, template_id, values, highlight = False, own = False):
	if highlight:
		generic_type = mtype + "_highlight"
	elif own:
		generic_type = mtype + "_own"
		template_id = template_id + "_own"
	else:
		generic_type = mtype

	values["time"] = time.strftime(config.get("templates", "datestring"))

	base_color = config.get("colors", generic_type, "default")
	template = config.get("templates", template_id)

	msg = FormattedMessage(mtype, template, values, base_color, highlight, own)

	if None == template:
		msg.template = "TEMPLATE_ERROR(%s)" % template_id

	return msg

@types(msg = (basestring, list, FormattedMessage))
def print_tab(dest_tab, msg, msgtype="informative"):
	if not main_window:
		raise ValueError, "No main_window found."

	tablist = tabs.tree_to_list(main_window.servers)

	try:
		i = tablist.index(dest_tab)

	except ValueError:
		print_error("print_tab to invalid destinaton '%s'." % dest_tab)
		return

	else:
		if isinstance(msg, FormattedMessage):
			markup = msg.markup()
			if isinstance(markup,tuple):
				# ("...",[(color,pos),...])
				new_markup = helper.markup.tuple_to_list(markup)
				textItem = urwid.Text(new_markup)
			elif isinstance(markup,list):
				# [(color,text),...]
				textItem = urwid.Text(markup)
			else:
				textItem = urwid.Text(markup)
		else:
			textItem = urwid.Text(msg)

		tablist[i].output_walker.append(textItem)

		if main_window.current_tab != dest_tab:
			if isinstance(msg, FormattedMessage):
				dest_tab.add_status(msg.category)
			else:
				dest_tab.add_status(msgtype)
			main_window.update_divider()
		else:
			main_window.body.scroll_to_bottom()

def print_tab_notification(tab, msg):
	print_tab(tab, "*** Notification: " + msg)

def print_tab_error(tab, msg):
	print_tab(tab, "!!! Error: " + msg)

def print_normal(msg, *args, **dargs):
	main_window.print_text(msg)

def print_error (msg, *args, **dargs):
	main_window.print_text("!!! Error: " + msg)

def print_notification (msg):
	main_window.print_text("*** Notification: " + msg)

def print_debug (msg, *args, **dargs):
	if not config.get_bool("nigiri", "show_debug"):
		return
	main_window.print_text("=== Debug: " + msg)
