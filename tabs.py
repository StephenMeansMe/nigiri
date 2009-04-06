from typecheck import types

from urwid import Signals, MetaSignals

# TODO:  method to get a generic list of
# TODO:: tabs. (from tree to list)

class Tab(object):

	__metaclass__ = MetaSignals
	signals = ["add_child", "remove_child"]

	_name = ""
	_connected = False
	_parent = None
	_status = {}

	input_history = None
	output_walker = None

	@types(name = str)
	def __init__(self, name):
		self._name = name

	@types(switch = str)
	def set_connected(self, switch):
		self._connected = switch

	def child_added(self, child):
		Signals.emit(self, "child_added", child)

	def child_removed(self, child):
		Signals.emit(self, "child_removed", child)

	def set_parent(self, parent):
		try:
			self._parent.child_removed(self)
		except AttributeError:
			pass

		self._parent = parent

		try:
			self._parent.child_added(self)
		except AttributeError:
			pass

	def get_parent(self):
		return self._parent

	@types(name = str)
	def add_status(self, name):
		self._name[name] = True

	@types(name = str)
	def remove_status(self, name):
		try:
			del self._status[name]
		except KeyError:
			pass

	def reset_status(self):
		self._status = []

class Server(Tab):

	_nick = ""
	_away = ""
	_channels = []

	def __init__(self, name):
		Tab.__init__(self, name)

	@types(nick = str)
	def set_nick(self, nick):
		self._nick = nick

	def get_nick(self):
		return self._nick

	@types(msg = str)
	def set_away(self, msg):
		self._away = msg

	def child_added(self, child):
		Tab.child_added(self, child)
		self._channels.append(child)

	def child_removed(self, child):
		Tab.child_removed(self, child)
		try:
			i = self._channels.index(child)
		except ValueError:
			pass
		else:
			del self._channels[i]

class Channel(Tab):

	_topic = ""
	_channels = {}

	@types(name = str)
	def __init__(self, name, parent = None):
		Tab.__init__(self, name)
		self.set_parent(parent)

	@types(topic = str)
	def set_topic(self, topic):
		self._topic = topic

	def get_topic(self):
		return self._topic

class Query(Tab):

	def __init__(self, name, parent = None):
		Tab.__init__(self, name)
		self.set_parent(parent)
