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

import config
#import log
from typecheck import types

main_window = None
#generic_log = None

class error(object): pass
class debug(object): pass
class notification(object): pass

def setup ():
	try:
		from __main__ import main_window as mw
	except ImportError,e:
		print "Error while initializing messages module: '%s'" % (e)
		sys.exit (1)
	global main_window#, generic_log
	main_window = mw
#	generic_log = log.Logger ("nigiri")

@types (type=type, message=str)
def handle_message (type, message):
	destinations = config.get_list("messages",type.__name__)

	if not destinations:
		# no destionations are given, no print
		return

	for dest in destinations:
		if dest == "window":
			if not main_window and "stdout" not in destinations:
				print message
			elif main_window:
				main_window.print_text (message)

#		elif dest == "log":
#			generic_log.write (message)

		elif dest == "stdout":
			print message

@types (type=type, prefix=str, msg=str)
def printit (type, prefix, msg, *args, **dargs):
	msg = prefix + msg
	handle_message (type, msg)

@types (msg=str)
def print_error (msg, *args, **dargs):
	printit (error, "!!! Error: ", msg, *args, **dargs)

@types (msg=str)
def print_notification (msg, *args, **dargs):
	printit (notification, "*** Notification: ", msg, *args, **dargs)

@types (msg=str)
def print_debug (msg, *args, **dargs):
	printit (debug, "=== Debug: ", msg, *args, **dargs)
