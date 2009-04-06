import urwid
import ansi

class ExtendedText(urwid.Text):

	markup = []
	use_markup = True

	def append(self, text):
		markup = ansi.parse_markup (text)
		self.markup += markup

		self.set_text(self.markup)

	def set_text(self, input):
		if type(input) == type(""):
			markup = ansi.parse_markup (input)

		else:
			markup = input

		urwid.Text.set_text (self, markup)
