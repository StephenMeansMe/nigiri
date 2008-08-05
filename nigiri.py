#!/usr/bin/env python
"""
Copyright (c) 2008 Peter Hladik
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

from dbus.mainloop.glib import DBusGMainLoop
import dbus
import gobject
import threading
import sys
import time
import signals
import commands

class Nigiri(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.servers = []
    self.channels = {}
    self.nicks = {}
    self.own_nicks = {}
    self.current_server = "euirc" # TODO
    self.current_channel = "#Inkirei" # TODO
    self.commandlist = commands.get_commandlist()
    self.connection_retries = 12 # TODO client-config
    self.bus = None
    self.proxy = None
    self.loop = None
    self.start_client()

  def run(self):
    try:
      self.loop.run()
    except KeyboardInterrupt:
      self.loop.quit()

  def stop(self):
    self._Thread__stop()
    self.loop.quit()

  def start_client(self):
    print "connecting to dbus..."
    DBusGMainLoop(set_as_default=True)
    gobject.io_add_watch(sys.stdin, gobject.IO_IN | gobject.IO_ERR | gobject.IO_HUP, commands.input_handler, self)
    self.loop = gobject.MainLoop()
    self.bus = dbus.SessionBus()

    print "starting signal processing..."
    self.signals = signals.Signals(self)

    retry = 0
    while self.proxy == None and retry < self.connection_retries:
      print "connecting to maki..."
      try:
        self.proxy = self.bus.get_object("de.ikkoku.sushi", "/de/ikkoku/sushi")
      except dbus.DBusException:
        retry += 1
        if retry < self.connection_retries:
          time.sleep(5)
          print "retry",
        else:
          print "connection failed!"
          sys.exit(1)

    print "retrieve information from maki"
    commands.servers(self, "")
    commands.own_nick(self, "")
    for server in self.servers:
      commands.channels(self, server)

if __name__ == "__main__":
  nigiri = Nigiri()
  nigiri.start()

# vi:tabstop=2:shiftwidth=2:expandtab
