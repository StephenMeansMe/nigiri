from typecheck import types

from urwid import Signals, MetaSignals, SimpleListWalker

def tree_to_list(input_parents, target = None):

	l = []

	for parent in input_parents:

		if target and parent != target:
			continue

		for child in target.children:
			l.append(child)

	return l

class Tab(object):

	__metaclass__ = MetaSignals
	signals = ["add_child", "remove_child"]

	_name = ""
	_connected = False
	_parent = None
	_status = {}

	children = []
	input_history = None
	output_walker = SimpleListWalker([])

	def __repr__(self):
		return self._name

	def __str__(self):
		return self._name

	@types(name = str)
	def __init__(self, name):
		self._name = name

	@types(switch = str)
	def set_connected(self, switch):
		self._connected = switch

	def child_added(self, child):
		Signals.emit(self, "child_added", child)
		self.children.append(child)

	def child_removed(self, child):
		Signals.emit(self, "child_removed", child)
		try:
			i = self.children.index(child)
		except ValueError:
			pass
		else:
			del self.children[i]


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

	@types(status = str)
	def has_status(self, status):
		return self._status.has_key(status)

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
