import urwid

class ExtendedListBox(urwid.ListBox):

	def __init__(self, body):
		urwid.ListBox.__init__(self, body)

	def set_body(self, body):
		if self.body:
			urwid.Signals.disconnect(body, "modified", self._invalidate)

		self.body = body
		self._invalidate()

		urwid.Signals.connect(body, "modified", self._invalidate)

	def scroll_to_bottom (self, size):
		while self.keypress (size, "down") != "down":
			pass


