# coding: UTF-8
"""
Copyright (c) 2008 Marian Tietz
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

import sushi

plugin_info = (
	"Writes the current playing song to the channel after typing /np",
	"0.1",
	"Marian Tietz"
)

class np (sushi.Plugin):

	def __init__(self):
		sushi.Plugin.__init__(self, "np")

		self.add_command("np", self.np_command)

		# valid players are mpd and decibel
		self.audio_player = "mpd"
		# valid format vars are artist, title and album
		self.format_string = "np: %(artist)s - %(title)s"

		self.mpd_host = "192.168.1.1"
		self.mpd_port = 6600
		self.mpd_password = "fh482"

	def unload(self):
		self.remove_command("np")

	def get_mpd_info(self):
		try:
			import mpd
		except ImportError:
			self.display_error("mpd module not found.")
			return None

		client = mpd.MPDClient()

		try:
			client.connect(self.mpd_host, self.mpd_port)
		except:
			return None

		if self.mpd_password:
			client.password(self.mpd_password)

		data = {"artist":"N/A","title":"N/A","album":"N/A"}
		data.update(client.currentsong())

		try:
			s = self.format_string % data
		except:
			display_info("Error while formatting format string.")
			return None

		client.disconnect()

		return s

	def get_decibel_info(self):
		import os
		from xdg.BaseDirectory import xdg_config_home

		try:
			f = open(os.path.join(
				xdg_config_home,
				"decibel-audio-player",
				"now-playing.txt"))
			s = f.read().replace("\n", " ")
			f.close()
		except:
			self.display_error("can't get decibel infos.")
			return None
		else:
			return "np: %s" % (s)
		return None

	def np_command(self, server, target, args):

		if not (server and target):
			return

		if self.audio_player == "mpd":
			info = self.get_mpd_info()

			if info == None:
				self.display_error("Error while retrieving infos from mpd.")
				return

		elif self.audioplayer == "decibel":

			info = self.get_decibel_info()

			if info == None:
				self.display_error("Error while retrieving infos from decibel.")
				return

		else:
			display_error("Unknown player given ('%s')" % (self.audioplayer))
			return

		bus = self.get_bus()

		if not bus:
			self.display_error("No connection to maki.")
		else:
			import messages
			messages.print_debug("server = '%s', target = '%s', info = '%s'" % (server, target, info))
			bus.message(server, target, info)
