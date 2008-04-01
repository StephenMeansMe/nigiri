############################################
##  Licence: Public Domain
############################################

import time

# TODO: time-format dependend on client configuration
def timestamp(line, timestamp):
  return time.strftime("[%H%M%S] ", time.localtime(timestamp)) + line

def add_all(bus):
  print "adding signals..."
  bus.add_signal_receiver(message, "message")
  bus.add_signal_receiver(action, "action")
  bus.add_signal_receiver(ctcp, "ctcp")
  bus.add_signal_receiver(away, "away")
  bus.add_signal_receiver(away_message, "away_message")
  bus.add_signal_receiver(back, "back")
  bus.add_signal_receiver(join, "join")
  bus.add_signal_receiver(part, "part")
  bus.add_signal_receiver(kick, "kick")
  bus.add_signal_receiver(mode, "mode")
  bus.add_signal_receiver(nick, "nick")
  bus.add_signal_receiver(connect, "connect")
  bus.add_signal_receiver(connected, "connected")
  bus.add_signal_receiver(reconnect, "reconnect")
  bus.add_signal_receiver(quit, "quit")
  bus.add_signal_receiver(shutdown, "shutdown")

###
# Signal Handlers
###
def message(time, server, nick, target, message):
  "Wichtig: Auch eigene Nachrichten werden an die Clients geschickt, um mehrere parallele Clients zu ermoeglichen."
  print timestamp("<%s> %s" % (nick, message), time)

def notice(time, server, nick, target, message):
  print timestamp("<<%s>> %s" % (nick, message), time)

def action(time, server, nick, target, message):
  print timestamp("*%s %s*" % (nick, message), time)

def ctcp(time, server, nick, target, message):
  print timestamp("??? ctcp-request for %s by %s" % (message, nick), time)

def away(time, server):
  print timestamp("You have been marked as being away", time)

def away_message(time, server, nick, message):
  print timestamp("%s is away (reason: %s)" % (nick, message), time)

def back(time, server):
  print timestamp("You are no longer marked as being away", time)

def join(time, server, nick, channel):
  "prints information about joins in the respective channels"
  print timestamp(">>> %s joined %s on %s" % (nick, channel, server), time)

def part(time, server, nick, channel, message):
  "message ist optional und kann leer (\"\") sein."
  print timestamp("<<< %s has left %s (reason: %s)" % (nick, channel, message), time)

def kick(time, server, nick, channel, who, message):
  "message ist optional und kann leer (\"\") sein."
  print timestamp("-!- %s has been kicked by %s (reason: %s)" % (who, nick, message), time)

def nick(time, server, nick, new_nick):
  print timestamp("-!- %s is now known as %s" % (nick, new_nick), time)

def mode(time, server, nick, target, mode, parameter):
  print timestamp("-!- mode of %s changed for %s by %s" % (parameter, mode, nick), time)

def connect(time, server):
  "Wird gesendet, wenn eine erfolgreiche Verbindung zum IRC-Server aufgebaut wurde."
  print timestamp("/// client is trying to connect to %s" % server, time)

def reconnect(time, server):
  "Wird gesendet, wenn ein Wiederverbindungsversuch stattfindet."
  print timestamp("\\\\\\ client is trying to reconnect to %s" % server, time)

def connected(time, server, nick):
  "Wird gesendet, wenn ein Login auf dem IRC-Server stattgefunden hat. nick ist dabei der eigene Nickname."
  print timestamp("/// client is now connected to %s" % server, time)
  print timestamp("    nick is set to %s" % nick, time)

def motd(time, server, message):
  print message

def quit(time, server, nick, message):
  "message ist optional und kann leer (\"\") sein."
  print timestamp("<<< %s has quit (reason: %s)" % (nick, message), time)

def shutdown(time):
  "Wird gesendet, wenn maki beendet wird."
  print timestamp("!!! client is being shut down", time)
