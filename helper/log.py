# coding: UTF-8
"""
Copyright (c) 2009 Marian Tietz
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE AUTHORS AND CONTRIBUTORS ``AS IS'' AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.
"""

import os
import sys
import time
from typecheck import types

from xdg.BaseDirectory import xdg_data_home

class Logger (object):

	_path = ""
	_file = None

	def __init__ (self, filename, open=True):
		self._set_path (filename)

		if open: self.open ()

	def open (self):
		""" open the log file and write start message to it """
		if not self._check_path ():
			return False

		self._file = file (self._path, "a+")

		timestamp = time.strftime (
			">>> Logging started at %H:%M on %d. %b %Y.")

		self.write (timestamp+"\n")

		return True

	def get_path(self):
		return self._path

	def silent_close (self):
		if self._file or self._file.closed:
			self._file.close()

	def close (self):
		""" write stop text to file and close it """

		if self._file:
			self.write ("%s\n" % (time.strftime (
				">>> Logging stopped at %H:%M on %d. %b. %Y.")))
			self.silent_close ()

	@types (text=str)
	def write (self, text):
		""" write timestamp plus text to log file """

		if not self._file or self._file.closed or not text:
			return

		try:
			self._file.write (text)
		except ValueError:
			# despite of is-closed-check, file is closed
			return

	@types (lines=int)
	def read (self, lines):
		if not self._file or self._file.closed:
			return None

		# TODO: implement this
		return ()

	def _set_path (self, filename):
		self._path = os.path.join (
			xdg_data_home,
			"sushi",
			filename)

	def _check_path (self):
		""" check for every dir on the way
			to the log file and create it
			if not found.
		"""
		path, file = os.path.split(self._path)

		if not os.path.exists (path):
			# create the directories
			try:
				os.makedirs (path)
			except os.error, e:
				print "Error while creating neccessary directories: %s"\
					% (e)
				return False

		if not os.path.exists(os.path.join(path, file)):
			try:
				f = open (self._path, "w")
			except BaseException,e:
				print "Error while creating error log file: %s" % (e)
				return False
			else:
				f.close()

			return True
		else:
			return True
		return False

	def _handle_main_quit (self):
		self.close()
