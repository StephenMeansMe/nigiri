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
#import log
from typecheck import types
import tabs

main_window = None
#generic_log = None

class error(object): pass
class debug(object): pass
class notification(object): pass
class normal(object): pass

class tab(object): pass
class tab_error(object): pass
class tab_notification(object):	pass
class tab_debug(object): pass

def setup (mw):
	global main_window#, generic_log
	main_window = mw
#	generic_log = log.Logger ("nigiri")


def format_message(type, msg, **fmt):
	template = config.get("formats", type)

	if not template:
		print_error("No format template for type '%s'." % (type))
		return

	if not fmt.has_key("datestring"):
		fmt["datestring"] = time.strftime(config.get("formats","datestring"))

	fmt["message"] = msg

	return template % fmt

@types (mclass=type, message=(str, unicode))
def handle_message (mclass, org_message, **dargs):
	""" associate the message class to the
		configured destinations and leave the
		message there.
		If the given message is markupped, the
		markup is striped if the destination
		is not "window".
	"""
	destinations = config.get_list("messages", mclass.__name__)

	if not destinations:
		# no destionations are given, no print
		return

	for dest in destinations:
		if dest != "window" and dargs.has_key("markup"):
			# text is markupped, convert it to plain text
			message, attr = urwid.util.decompose_tagmarkup(message)
		else:
			# window output can display markupped messages
			message = org_message

		if dest == "window":
			if not main_window and "stdout" not in destinations:
				print message
			elif main_window:
				main_window.print_text (message)

#		elif dest == "log":
#			generic_log.write (message)

		elif dest == "stdout":
			print message

@types(msg = (str,unicode))
def print_to_tab(dest_tab, msg):
	if not main_window:
		return

	tablist = tabs.tree_to_list(main_window.servers)

	try:
		i = tablist.index(dest_tab)
	except ValueError:
		print_error("print_tab to invalid destinaton '%s'." % dest_tab)
		return
	else:
		tablist[i].output_walker.append(urwid.Text(msg))

@types (mclass=type, prefix=str, msg=(str,unicode,list))
def printit (mclass, prefix, msg, *args, **dargs):

	if type(msg) == list:
		dargs["markup"] = True
		msg = [prefix] + msg
	else:
		msg = prefix + msg

	try:
		dest_tab = dargs["dest_tab"]
	except KeyError:
		pass
	else:
		if not dest_tab:
			print_error("dest_tab is None. ('%s')" % (msg))
			return

		print_to_tab(dest_tab, msg)

		if main_window.current_tab != dest_tab:
			try:
				msgtype = dargs["type"]
			except KeyError:
				msgtype = "message"

			dest_tab.add_status(msgtype)
			main_window.update_divider()
		else:
			main_window.body.scroll_to_bottom(
				main_window.ui.get_cols_rows())

	if dargs.has_key("dont_handle") and dargs["dont_handle"]:
		return

	handle_message (mclass, msg, **dargs)

def print_normal(msg, *args, **dargs):
	printit(normal, "", msg, *args, **dargs)

def print_error (msg, *args, **dargs):
	printit (error, "!!! Error: ", msg, *args, **dargs)

def print_notification (msg, *args, **dargs):
	printit (notification, "*** Notification: ", msg, *args, **dargs)

def print_debug (msg, *args, **dargs):
	printit (debug, "=== Debug: ", msg, *args, **dargs)


def print_tab(dest_tab, msg, *args, **dargs):
	dargs.update({"dest_tab":dest_tab})
	printit(tab, "", msg, *args, **dargs)

def print_tab_error(dest_tab, msg, *args, **dargs):
	dargs.update({"dest_tab":dest_tab})
	printit(tab_error, "!!! Error: ", msg, *args, **dargs)

def print_tab_notification(dest_tab, msg, *args, **dargs):
	dargs.update({"dest_tab":dest_tab})
	printit(tab_notification, "*** Notification: ", msg, *args, **dargs)

def print_tab_debug(dest_tab, msg, *args, **dargs):
	dargs.update({"dest_tab":dest_tab})
	printit(tab_debug, "=== Debug: ", msg, *args, **dargs)
