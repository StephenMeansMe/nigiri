from typecheck import types
from dbus import String

from urwid import Signals, MetaSignals, SimpleListWalker

def tree_to_list(input_parents, target = None):

	l = []

	for parent in input_parents:

		if target and parent != target:
			continue

		for child in parent.children:
			l.append(child)

	return l

class Tab(object):

	__metaclass__ = MetaSignals
	signals = ["child_added", "child_removed", "remove"]

	_valid_stati = ["highlight","highlight_action",
		"new_action","new_message"]

	_name = ""
	_connected = False
	_parent = None
	_status = {}

	children = []
	input_history = None
	output_walker = SimpleListWalker([])

	def __repr__(self):
		return "<tab: %s:%s>" % (self._parent, self._name)

	def __str__(self):
		return self._name

	@types(name = (String, str))
	def __init__(self, name):
		self._name = name

	@types(switch = str)
	def set_connected(self, switch):
		self._connected = switch

	def child_added(self, child):
		Signals.emit(self, "child_added", self, child)
		self.children.append(child)

	def child_removed(self, child):
		Signals.emit(self, "child_removed", self, child)
		try:
			i = self.children.index(child)
		except ValueError:
			pass
		else:
			del self.children[i]

	def set_parent(self, parent):
		if parent in self.children:
			print "Loop detected in '%s'.set_parent(%s)" % (
				self, parent)
			return

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

	def remove(self):
		""" emit remove signals """
		for child in self.children:
			child.remove()
			self.child_removed(child)
		Signals.emit("remove", self)

	@types(name = str)
	def add_status(self, name):
		if name in self._valid_stati:
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

	@types(name = (String,str))
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
