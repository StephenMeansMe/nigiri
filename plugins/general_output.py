import logging
import urwid

import sushi
import __main__
from extends.ListBox import ExtendedListBox

plugin_info = ("Marian Tietz",
				"1.0",
				"Adds a widget which displays every message received.")

class GeneralOutputWidget(ExtendedListBox):

	def __init__(self, sushi, *args, **kwargs):
		self.text_walker = urwid.SimpleListWalker([])

		ExtendedListBox.__init__(self, self.text_walker, *args, **kwargs)

		self.sushi = sushi
		self._connect_signals()

	def _connect_signals(self):
		self.sushi.connect_to_signal("message", self._message_cb)

	def _message_cb(self, time, server, target, sender, message):
		self.text_walker.append(urwid.Text(target+": "+message))
		self.scroll_to_bottom()


class ProxyFrame(urwid.Frame):

	def __init__(self, *args, **kwargs):
		urwid.Frame.__init__(self, *args, **kwargs)
		logging.debug("args = %s" % (args,))

	def __getattribute__(self, attr):

		def from_frame_body(attr):
			body = urwid.Frame.__getattribute__(self, "_body")
			return getattr(body, attr)

		try:
			# return Frame attribute
			logging.debug("requesting %s" % (attr))
			return urwid.Frame.__getattribute__(self, attr)
		except AttributeError, e:
			# if this fails, return from Frame.body
			logging.debug("forwarding %s" % (attr))
			return from_frame_body(attr)



class general_output(sushi.Plugin):
	""" Nigiri plugin.

		Adds a widget bove of the body widget
		which displays every message received
		regardless of the active tab.
	"""

	def __init__(self, *args, **kwargs):
		sushi.Plugin.__init__(self, "general_output")

		self._applied = False
		self.append_general_output()

	def append_general_output(self):
		self.output = GeneralOutputWidget(self.get_bus())

		body = __main__.main_window.body
		self.original_body = body

		__main__.main_window.body = ProxyFrame(body, header=urwid.BoxAdapter(self.output, 5))
		__main__.main_window._setup_context()

		self._applied = True

	def maki_connected(self, sushi):
		pass

	def maki_disconnected(self, sushi):
		pass

	def unload(self):
		if self._applied:
			__main__.main_window.body = self.original_body

