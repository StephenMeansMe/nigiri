from dbus.mainloop.glib import DBusGMainLoop
import dbus
import gobject
import threading
from output import *

def start():
  DBusGMainLoop(set_as_default=True)
  loop = gobject.MainLoop()
  
  bus = dbus.SessionBus()
  proxy = bus.get_object("de.ikkoku.sushi", "/de/ikkoku/sushi")
  bus.add_signal_receiver(message, "message")
  bus.add_signal_receiver(action, "action")
  bus.add_signal_receiver(away, "away")
  bus.add_signal_receiver(away_message, "away_message")
  bus.add_signal_receiver(back, "back")
  bus.add_signal_receiver(join, "join")
  bus.add_signal_receiver(part, "part")
  bus.add_signal_receiver(kick, "kick")
  bus.add_signal_receiver(nick, "nick")
  bus.add_signal_receiver(connect, "connect")
  bus.add_signal_receiver(connected, "connected")
  bus.add_signal_receiver(reconnect, "reconnect")
  bus.add_signal_receiver(quit, "quit")
  
  loop.run()

start()
