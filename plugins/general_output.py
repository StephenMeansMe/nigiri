import time # strftime
import logging
import urwid

import connection
import sushi
import __main__
from extends.ListBox import ExtendedListBox

plugin_info = ("Marian Tietz",
				"1.0",
				"Adds a widget which displays every message received.")

class GeneralOutputWidget(ExtendedListBox):

	def __init__(self, plugin, *args, **kwargs):
		self.text_walker = urwid.SimpleListWalker([])

		ExtendedListBox.__init__(self, self.text_walker, *args, **kwargs)

		self.plugin = plugin
		self._connect_signals()

	def _connect_signals(self):
		self.plugin.connect_signal("message", self._message_cb)

	def _message_cb(self, timestamp, server, sender, target, message):
		if not target:
			locationFormat = server
		else:
			locationFormat = server+":"+target

		format = "[%(timestamp)s] (%(location)s) <%(nick)s> %(message)s" % {
			"timestamp": time.strftime("%H:%M", time.localtime(timestamp)),
			"location": locationFormat,
			"nick": connection.parse_from(sender)[0],
			"message": message}

		self.text_walker.append(urwid.Text(format))
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
		self.output = GeneralOutputWidget(self)

		body = __main__.main_window.body
		self.original_body = body

		__main__.main_window.body = ProxyFrame(body, header=urwid.LineBox(urwid.BoxAdapter(self.output, 5)))
		__main__.main_window._setup_context()
		__main__.main_window.main_loop.widget = __main__.main_window.context

		self._applied = True

	def unload(self):
		if self._applied:
			__main__.main_window.body = self.original_body
			__main__.main_window._setup_context()
		sushi.Plugin.unload(self)

