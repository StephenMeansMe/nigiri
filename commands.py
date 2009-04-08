
from typecheck import types
from messages import print_notification, print_error
import config

import connection

def no_connection():
	if not connection.is_connected():
		print_error("No connection to maki.")
		return True
	return False

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

def cmd_echo(main_window, argv):
	""" /echo <text> """
	main_window.print_text(" ".join(argv[1:])+"\n")

def cmd_maki(main_window, argv):
	""" /maki [connect|shutdown] """
	def usage():
		print_notification("Usage: /maki [connect|shutdown]")

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

def cmd_python(main_window, argv):
	""" /python <code> """
	print_notification ("python: Executing...\n")
	try:
		exec(" ".join(argv[1:]))
	except BaseException,e:
		print_error ("python:  Error: %s\n" % (e))

def cmd_quit(main_window, argv):
	""" /quit """
	main_window.quit()

_command_dict = {
	"close": cmd_close,
	"connect": cmd_connect,
	"echo": cmd_echo,
	"maki": cmd_maki,
	"python": cmd_python,
	"quit": cmd_quit,
}

_builtins = _command_dict.keys()

@types (cmd=str)
def strip_command_char (cmd):
	if not cmd: return cmd
	if cmd[0] != config.get("nigiri","command_char"):
		return cmd
	return cmd[1:]

@types (text=str)
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

@types (name=str, fun=type(lambda:""))
def add_command(name, fun):
	global _command_dict
	if _command_dict.has_key (name):
		return False
	_command_dict[name] = fun

@types (name=str)
def remove_command(name):
	global _command_dict
	if _command_dict.has_key (name) and name not in _builtins:
		del _command_dict[name]
		return True
	return False
