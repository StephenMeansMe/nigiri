import urwid

class ExtendedBoxAdapter (urwid.BoxAdapter):

	def set_height (self, rows):
		self.height = rows
		self._invalidate()

