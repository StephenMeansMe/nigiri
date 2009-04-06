import urwid

import debug

class ExtendedEdit (urwid.Edit):

	hide_edit_text = False

	def set_hide (self, s):
		if type (s) != bool:
			raise TypeError, "Wrong type for s, bool required"
		self.hide_edit_text = s

	def get_text (self):

		if self.hide_edit_text:
			edit_text = len(self.edit_text)*"*"
		else:
			edit_text = self.edit_text

		return self.caption + edit_text, self.attrib
