import connection
import commands
import signals
import config
import tabs
import messages
import __main__

# XXX:  maybe better proxy both, commands and signals,
# XXX:: to catch errors in the error code.

class Plugin (object):

	def __init__(self, plugin_name):
		self._plugin_name = plugin_name

	def get_bus(self):
		return connection.sushi

	def get_nick(self, server):
		server_tab = __main__.main_window.find_server(server)
		if not server_tab:
			return None

		nick = server_tab.get_nick()

		if not nick:
			return None

		return nick

	def add_command(self, command, func):
		def func_proxy (main_window, argv):
			ct = main_window.current_tab

			if not ct:
				server_name = ""
				target_name = ""
			elif type(ct) == tabs.Server:
				server_name = ct.name
				target_name = ""
			else:
				server_name = tabs.get_server(ct).name
				target_name = ct.name

			return func(server_name, target_name, argv[1:])

#		self.emit("command_add", command, func)
		return commands.add_command(command, func_proxy)

	def remove_command(self, command):
#		self.emit("command_remove", command, func)
		return commands.remove_command(command)

	def connect_signal(self, signal, func):
#		self.emit("signal_connect", signal, func)
		return signals.connect_signal(signal, func)

	def disconnect_signal(self, signal, func):
#		self.emit("signal_disconnect", signal, func)
		return signals.disconnect_signal(signal, func)

	def set_config(self, name, value):
		section = "plugin_%s" % (self._plugin_name)

		config.create_section(section)

		return config.set(section, name, value)

	def get_config(self, name):
		section = "plugin_%s" % (self._plugin_name)

		return config.get(section, name)

	def display_error(self, error):
		messages.print_error("%s: %s" % (self._plugin_name,error))
