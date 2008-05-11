# vi:tabstop=2:shiftwidth=2:expandtab
############################################
##  Licence: Public Domain
############################################

import time

# TODO: time-format dependend on client configuration
def timestamp(line, timestamp):
  return time.strftime("[%H%M%S] ", time.localtime(timestamp)) + line

###
# Signal Handlers
###
class Signals:
  def __init__(self, nigiri):
    self.nigiri = nigiri
    self.nigiri.bus.add_signal_receiver(self.message, "message")
    self.nigiri.bus.add_signal_receiver(self.own_message, "own_message")
    self.nigiri.bus.add_signal_receiver(self.query, "query")
    self.nigiri.bus.add_signal_receiver(self.own_query, "own_query")
    self.nigiri.bus.add_signal_receiver(self.notice, "notice")
    self.nigiri.bus.add_signal_receiver(self.action, "action")
    self.nigiri.bus.add_signal_receiver(self.ctcp, "ctcp")
    self.nigiri.bus.add_signal_receiver(self.away, "away")
    self.nigiri.bus.add_signal_receiver(self.away_message, "away_message")
    self.nigiri.bus.add_signal_receiver(self.back, "back")
    self.nigiri.bus.add_signal_receiver(self.join, "join")
    self.nigiri.bus.add_signal_receiver(self.part, "part")
    self.nigiri.bus.add_signal_receiver(self.kick, "kick")
    self.nigiri.bus.add_signal_receiver(self.nick, "nick")
    self.nigiri.bus.add_signal_receiver(self.mode, "mode")
    self.nigiri.bus.add_signal_receiver(self.connect, "connect")
    self.nigiri.bus.add_signal_receiver(self.reconnect, "reconnect")
    self.nigiri.bus.add_signal_receiver(self.connected, "connected")
    self.nigiri.bus.add_signal_receiver(self.topic, "topic")
    self.nigiri.bus.add_signal_receiver(self.motd, "motd")
    self.nigiri.bus.add_signal_receiver(self.quit, "quit")
    self.nigiri.bus.add_signal_receiver(self.shutdown, "shutdown")

  def message(self, time, server, nick, target, message):
    print timestamp("<%s> %s" % (nick, message), time)

  def own_message(self, time, server, target, message):
    print timestamp("<%s> %s" % (self.nigiri.own_nicks[server], message), time)

  def query(self, time, server, nick, message):
    print timestamp("<%s> %s" % (nick, message), time)

  def own_query(self, time, server, target, message):
    print timestamp("<%s> %s" % (self.nigiri.own_nicks[server], message), time)

  def notice(self, time, server, nick, target, message):
    print timestamp("<<%s>> %s" % (nick, message), time)

  def action(self, time, server, nick, target, message):
    print timestamp("*%s %s*" % (nick, message), time)

  def ctcp(self, time, server, nick, target, message):
    print timestamp("??? ctcp-request for %s by %s" % (message, nick), time)

  def away(self, time, server):
    print timestamp("You have been marked as being away", time)

  def away_message(self, time, server, nick, message):
    print timestamp("%s is away (reason: %s)" % (nick, message), time)

  def back(self, time, server):
    print timestamp("You are no longer marked as being away", time)

  def join(self, time, server, nick, channel):
    "prints information about joins in the respective channels"
    print timestamp(">>> %s joined %s on %s" % (nick, channel, server), time)

  def part(self, time, server, nick, channel, message):
    "message ist optional und kann leer (\"\") sein."
    print timestamp("<<< %s has left %s (reason: %s)" % (nick, channel, message), time)

  def kick(self, time, server, nick, channel, who, message):
    "message ist optional und kann leer (\"\") sein."
    print timestamp("-!- %s has been kicked by %s (reason: %s)" % (who, nick, message), time)

  def nick(self, time, server, nick, new_nick):
    if nick == self.nigiri.own_nicks[server]:
      self.nigiri.own_nicks[server] = new_nick

    print timestamp("-!- %s is now known as %s" % (nick, new_nick), time)

  def mode(self, time, server, nick, target, mode, parameter):
    """nick ist optional und kann leer(\"\") sein.
       parameter ist optional und kann leer(\"\") sein."""
    if parameter != "":
      space = " "
    else:
      space = ""

    if nick == "":
      print timestamp("-!- current mode of %s [%s%s%s]" % (target, mode, space, parameter), time)
    else:
      print timestamp("-!- %s changed mode of %s [%s%s%s]" % (nick, target, mode, space, parameter), time)

  def connect(self, time, server):
    "Wird gesendet, wenn eine erfolgreiche Verbindung zum IRC-Server aufgebaut wurde."
    print timestamp("/// client is trying to connect to %s" % server, time)

  def reconnect(self, time, server):
    "Wird gesendet, wenn ein Wiederverbindungsversuch stattfindet."
    print timestamp("\\\\\\ client is trying to reconnect to %s" % server, time)

  def connected(self, time, server, nick):
    "Wird gesendet, wenn ein Login auf dem IRC-Server stattgefunden hat. nick ist dabei der eigene Nickname."
    self.nigiri.own_nicks[server] = nick
    print timestamp("/// client is now connected to %s" % server, time)
    print timestamp("    nick is set to %s" % nick, time)

  def topic(self, time, server, nick, channel, topic):
    "nick ist optional und kann leer (\"\") sein."
    if nick == "":
      print timestamp("||| the current topic is: %s" % topic, time)
    else:
      print timestamp("||| %s changed the topic to: %s" (nick, topic), time)

  def motd(self, time, server, message):
    print message

  def quit(self, time, server, nick, message):
    "message ist optional und kann leer (\"\") sein."
    print timestamp("<<< %s has quit (reason: %s)" % (nick, message), time)

  def shutdown(self, time):
    "Wird gesendet, wenn maki beendet wird."
    print timestamp("!!! client is being shut down", time)
