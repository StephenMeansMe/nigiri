import time

# TODO: time-format dependend on client configuration
def timestamp(line, timestamp):
  return time.strftime("[%H%M%S] ", time.localtime(timestamp)) + line

###
# Signal Handlers
###
def message(time, server, channel, nick, message):
  "Wichtig: Auch eigene Nachrichten werden an die Clients geschickt, um mehrere parallele Clients zu ermoeglichen."
  print timestamp("<%s> %s" % (nick, message), time)

def action(time, server, channel, nick, message):
  print timestamp("*%s %s*" % (nick, message), time)

def away(time, server):
  print timestamp("You have been marked as being away", time)

def away_message(time, server, nick, message):
  print timestamp("%s is away (reason: %s)" % (nick, message), time)

def back(time, server):
  print timestamp("You are no longer marked as being away", time)

def join(time, server, channel, nick):
  "prints information about joins in the respective channels"
  print timestamp(">>> %s joined %s on %s" % (nick, channel, server), time)

def part(time, server, channel, nick, message):
  "message ist optional und kann leer (\"\") sein."
  print timestamp("<<< %s has left %s (reason: %s)" % (nick, channel, message), time)

def kick(time, server, channel, nick, who, message):
  "message ist optional und kann leer (\"\") sein."
  print timestamp("-!- %s has been kicked by %s (reason: %s)" % (who, nick, message), time)

def nick(time, server, nick, new_nick):
  print timestamp("-!- %s is now known as %s" % (nick, new_nick), time)

def connect(time, server):
  "Wird gesendet, wenn eine erfolgreiche Verbindung zum IRC-Server aufgebaut wurde."
  print timestamp("/// client is trying to connect to %s" % server, time)

def reconnect(time, server):
  "Wird gesendet, wenn ein Wiederverbindungsversuch stattfindet."
  print timestamp("\\\\\\ client is trying to reconnect to %s" % server, time)

def connected(time, server, nick):
  "Wird gesendet, wenn ein Login auf dem IRC-Server stattgefunden hat. nick ist dabei der eigene Nickname."
  print timestamp("/// client is now connected to %s" % server, time)
  print timestamp("/// nick is set to %s" % nick)

def quit(time, server, nick, message):
  "message ist optional und kann leer (\"\") sein."
  print timestamp("<<< %s has quit (reason: %s)" % (nick, message), time)
