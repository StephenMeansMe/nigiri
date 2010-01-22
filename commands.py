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

from typecheck import types
from messages import print_notification, print_error, print_normal
from gettext import gettext as _
# TODO: use gettext

import tabs
import config
import signals
import connection
import plugin_control

def no_connection():
	if not connection.sushi.connected:
		print_error("No connection to maki.")
		return True
	return False

def send_text(tab, text):
	if no_connection() or type(tab) == tabs.Server or not text:
		return

	server_name = tab.parent.name

	if not tab.connected:
		print_error("Not connected to server "\
			"'%s'." % (server_name))
		return

	if type(tab) == tabs.Channel and not tab.joined:
		print_error("You are not on the channel "\
			"'%s'." % (tab.name))
		return

	connection.sushi.message(server_name, tab.name, text)

def cmd_add_server(main_window, argv):
	""" /add_server <name> <address> <port> <nick> <real> """
	if no_connection():
		return

	if len(argv) != 6:
		print_notification("Usage: /add_server <name> <address> "\
			"<port> <nick> <real>")
		return

	cmd, server_name, address, port, nick, name = argv

	try:
		int(port)
	except ValueError:
		print_error("Invalid value for 'port' given.")
		return

	if server_name in connection.sushi.server_list("",""):
		print_error("Server with name '%s' already existing." % (server_name))
		return

	pairs = (("address", address), ("port", port), ("nick", nick),
		("name", name))
	for key,value in pairs:
		connection.sushi.server_set(server_name, "server", key, value)

	print_notification("Server '%s' successfully added." % (server_name))

def cmd_clear(main_window, argv):
	""" /clear [<markup>] """
	if len(argv) == 2 and argv[1] == "markup":
		for tab in tabs.tree_to_list(main_window.servers):
			tab.reset_status()
		main_window.update_divider()
	else:
		del main_window.body.body[0:]

def cmd_close(main_window, argv):
	""" /close """
	# close the current tab
	if not main_window.current_tab:
		return

	to_delete = main_window.current_tab
	main_window.switch_to_next_tab()
	to_delete.remove()

def cmd_connect(main_window, argv):
	""" /connect <server> """
	if no_connection():
		return

	if len(argv) != 2:
		print_notification("Usage: /connect <server>")
		return

	if argv[1] not in connection.sushi.server_list("",""):
		print_error("connect: The server '%(server)s' is not known." % {
			"server": argv[1]})
		return

	connection.sushi.connect(argv[1])

def cmd_dcc(main_window, argv):
	""" /dcc chat <target>
	/dcc send <target> <path>
	/dcc list <type>
	/dcc remove <type> <id>
	"""
	if no_connection():
		return

	if len(argv) < 2:
		print_notification("Usage: /dcc accept|chat|send|list|remove")
		return

	server_tab = tabs.get_server(main_window.current_tab)

	if argv[1] == "send":
		if len(argv) < 4:
			print_notification("Usage: /dcc send <target> <path>")
			return

		connection.sushi.dcc_send(server_tab.name, argv[2], argv[3])
	elif argv[1] == "accept":
		def accepted_cb(time, id, *x):
			if id == int(argv[2]):
				print_notification(_("DCC action with id %(id)d accepted." % {
					"id": id}))
				signals.disconnect_signal("dcc_send", accepted_cb)

		if len(argv) < 3:
			print_notification("Usage: /dcc accept <id>")
			return

		signals.connect_signal("dcc_send", accepted_cb)
		connection.sushi.dcc_send_accept(int(argv[2]))
	elif argv[1] == "chat":
		pass
	elif argv[1] == "list":
		if len(argv) < 3:
			print_notification("Usage: /dcc list chat|send")
			return

		if argv[2] == "send":
			ids, servers, froms, filenames, sizes, progresses, speeds, statuses = connection.sushi.dcc_sends()

			for i in range(len(ids)):
				print_normal("#%(id)d: %(filename)s from/to %(from)s [%(server)s]: %(progress)d/%(size)d @ %(speed)d" % {
						"id": ids[i],
						"filename": filenames[i],
						"from": froms[i],
						"server": servers[i],
						"progress": progresses[i],
						"size": sizes[i],
						"speed": speeds[i]
					})
		elif argv[2] == "chat":
			pass
	elif argv[1] == "remove":
		if len(argv) < 4:
			print_notification("Usage: /dcc remove <type> <id>")
			return

		if argv[2] == "send":
			connection.sushi.dcc_send_remove(int(argv[3]))
		elif argv[2] == "chat":
			pass

def cmd_echo(main_window, argv):
	""" /echo <text> """
	main_window.print_text(" ".join(argv[1:])+"\n")

def cmd_help(main_window, argv):
	""" /help [<command>] """
	if len(argv) == 2:
		sCmd = argv[1]
	else:
		sCmd = None

	msg = ""

	for (name, value) in globals().items():
		cmd_name = name[4:]

		if name[0:4] == "cmd_":
			if sCmd and sCmd != cmd_name:
				continue

			msg += "%s:\n %s\n" % (cmd_name,
				(value.__doc__
				or "No documentation yet.").replace("\t", "   "))

			if sCmd and sCmd == cmd_name:
				break

	print_normal(msg)

def cmd_join(main_window, argv):
	""" /join <channel> [<key>] """
	key = ""

	if len(argv) == 3:
		cmd, channel, key = argv
	elif len(argv) == 2:
		cmd, channel = argv
	elif len(argv) == 1 and type(main_window.current_tab) == tabs.Channel:
		channel = main_window.current_tab.name
	else:
		print_notification("Usage: /join [<channel> [<key>]]")
		return

	server_tab = tabs.get_server(main_window.current_tab)

	if not server_tab:
		print_error("No tab active.")
		return

	connection.sushi.join(server_tab.name, channel, key)
	print_notification("Joining channel '%s'." % (channel))

def cmd_load(main_window, argv):
	if len(argv) != 2:
		print_notification("Usage: /load <filename>")
		return

	name = argv[1]

	if plugin_control.is_loaded(name):
		print_notification("Plugin '%s' already loaded." % (name))
		return

	if plugin_control.load(name):
		print_notification("Plugin '%s' successfully loaded." % (name))
	else:
		print_notification("Error while loading plugin '%s'." % (name))

def cmd_maki(main_window, argv):
	""" /maki [connect|shutdown] """
	def usage():
		print_notification("Usage: /maki [connect|disconnect|shutdown]")

	if len(argv) != 2:
		usage()
		return

	cmd = argv[1]

	if cmd == "connect":
		print_notification("Connection to maki...")

		if connection.connect():
			print_notification("Connection to maki etablished.")
		else:
			print_notification("Connection to maki failed.")
		main_window.update_divider()

	elif cmd == "disconnect":
		if no_connection():
			return

		connection.disconnect()
		print_notification("Disconnected from maki.")
		main_window.update_divider()

	elif cmd == "shutdown":
		if no_connection():
			return

		connection.sushi.shutdown(config.get("chatting", "quit_message"))
		main_window.update_divider()

	else:
		usage()
		return

def cmd_names(main_window, argv):
	""" /names """
	if no_connection():
		return
	ct = main_window.current_tab
	if type(ct) != tabs.Channel:
		print_error("You must be on a channel to use /names.")
		return
	connection.sushi.names(ct.parent.name, ct.name)

def cmd_overview(main_window, argv):
	""" /overview [<server>] """
	if no_connection():
		return

	if len(argv) == 2:
		if argv[1] not in [n.name for n in main_window.servers]:
			print_error("Server '%s' not found." % (argv[1]))
			return
		server_list = [main_window.find_server(argv[1])]
	else:
		server_list = main_window.servers

	print_normal("Begin overview.")

	for server in server_list:
		if server.connected:
			connected = "connected"
		else:
			connected = "not connected"

		print_normal("Server '%s' (%s)" % (server, connected))

		for child in server.children:
			if type(child) == tabs.Channel:
				if child.joined:
					joined = "joined"
				else:
					joined = "not joined"
				print_normal("- Channel '%s' (%s)" % (child.name, joined))
			else:
				print_normal("- Query '%s'" % (child.name))

	print_normal("End of overview.")

def cmd_part(main_window, argv):
	""" /part [<reason>] """
	if no_connection():
		return

	if len(argv) == 2:
		reason = " ".join(argv[1:])
	else:
		reason = ""

	ct = main_window.current_tab
	if type(ct) in (tabs.Server, tabs.Query):
		print_error("The current tab is not a channel.")
		return
	else:
		connection.sushi.part(ct.parent.name, ct.name, reason)

def cmd_python(main_window, argv):
	""" /python <code> """
	print_notification ("python: Executing...\n")
	try:
		exec(" ".join(argv[1:]))
	except BaseException,e:
		print_error ("python: %s\n" % (e))

def cmd_quit(main_window, argv):
	""" /quit """
	main_window.quit()

def cmd_remove_server(main_window, argv):
	""" /remove_server <name> """
	if no_connection():
		return

	if len(argv) != 2:
		print_notification("Usage: /remove_server <name>")
		return

	name = argv[1]

	if not name in connection.sushi.server_list("", ""):
		print_error("Server '%s' not known to maki." % (name))
		return

	connection.sushi.server_remove(name, "", "")
	print_notification("Server '%s' successfully removed." % (name))

def cmd_servers(main_window, argv):
	""" /servers """
	if no_connection():
		return

	active_servers = connection.sushi.servers()

	print_normal("Servers known to maki: ")
	for name in connection.sushi.server_list("",""):
		if name in active_servers:
			connected = "connected"
		else:
			connected = "not connected"
		print_normal("- '%s' (%s)" % (name, connected))

def cmd_unload(main_window, argv):
	if len(argv) != 2:
		print_notification("Usage: /unload <filename>")
		return
	name = argv[1]

	if not plugin_control.is_loaded(name):
		print_error("Plugin '%s' is not loaded." % (name))
		return

	if not plugin_control.unload(name):
		print_error("Failed to unload plugin '%s'." % (name))
	else:
		print_notification("Plugin '%s' successfully unloaded." % (name))

_command_dict = {
	"add_server": cmd_add_server,
	"clear": cmd_clear,
	"close": cmd_close,
	"connect": cmd_connect,
	"dcc": cmd_dcc,
	"echo": cmd_echo,
	"help": cmd_help,
	"j": cmd_join,
	"join": cmd_join,
	"load": cmd_load,
	"maki": cmd_maki,
	"names": cmd_names,
	"overview": cmd_overview,
	"part": cmd_part,
	"python": cmd_python,
	"quit": cmd_quit,
	"remove_server": cmd_remove_server,
	"servers": cmd_servers,
	"unload": cmd_unload
}

_builtins = _command_dict.keys()

def strip_command_char (cmd):
	if not cmd: return cmd
	if cmd[0] != config.get("nigiri","command_char"):
		return cmd
	return cmd[1:]

def parse(main_window, text):
	argv = text.split(" ")

	if (not argv
		or (argv[0]
			and argv[0][0] != config.get(
				"nigiri",
				"command_char"))):
		return False

	command = strip_command_char (argv[0])

	if not command:
		return False

	try:
		fun = _command_dict[command]
	except KeyError:
		print_error ("No such command '%s'.\n" % (command))
	else:
		fun (main_window, argv)

	return True

@types (name=basestring, fun=type(lambda:""))
def add_command(name, fun):
	global _command_dict
	if _command_dict.has_key (name):
		return False
	_command_dict[name] = fun
	return True

@types (name=basestring)
def remove_command(name):
	global _command_dict
	if _command_dict.has_key (name) and name not in _builtins:
		del _command_dict[name]
		return True
	return False
