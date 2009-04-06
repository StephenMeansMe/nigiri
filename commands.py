
from typecheck import types
from messages import print_notification, print_error
import config

def cmd_echo(main_window, argv):
	""" /echo <text> """
	main_window.print_text(" ".join(argv[1:])+"\n")

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
	"echo": cmd_echo,
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
