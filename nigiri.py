############################################
##  Licence: Public Domain
############################################

from dbus.mainloop.glib import DBusGMainLoop
import dbus
import gobject
import threading
import sys
import signals
import commands

class Nigiri(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)        
    self.servers = []
    self.channels = {}
    self.nicks = {}
    self.current_server = "euirc" # TODO
    self.current_channel = "#Inkirei" # TODO
    self.commandlist = commands.get_commandlist()
  
    print "connecting to dbus..."
    DBusGMainLoop(set_as_default=True)
    gobject.io_add_watch(sys.stdin, gobject.IO_IN | gobject.IO_ERR | gobject.IO_HUP, commands.input_handler, self)
    self.loop = gobject.MainLoop()
  
    self.bus = dbus.SessionBus()
    self.proxy = self.bus.get_object("de.ikkoku.sushi", "/de/ikkoku/sushi")

    signals.add_all(self.bus)

    print "starting signal processing..."

    commands.servers(self, "")
    for server in self.servers:
      commands.channels(self, server)
  def run(self):
    try:
      self.loop.run()
    except KeyboardInterrupt:
      self.loop.quit()

  def stop(self):
    self._Thread__stop()
    self.loop.quit()

if __name__ == "__main__":
  nigiri = Nigiri()
  nigiri.start()
