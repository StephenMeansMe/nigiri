# vi:tabstop=2:shiftwidth=2:expandtab
############################################
##  Licence: Public Domain
############################################

###
# DBus Methods
###

# TODO add descriptions to the help messages

# Connection
def servers(nigiri, args):
  """irc-call: /servers
dbus method: servers()"""
  if help_request_p(args):
    print servers.__doc__
  else:
    nigiri.servers = map(str, nigiri.proxy.servers())
    print "You are connected to the following servers:"
    for server in nigiri.servers:
      print " %s" % server
  return True



def channels(nigiri, args):
  """irc-call: /channels [<server>[,<servers>]]
dbus method: channels(server)
if no server is supplied the client will ask for channels on every connected server"""
  if help_request_p(args):
    print channels.__doc__
  else:
    serverlist = args.split(",")
    if serverlist == ['']:
      servers(nigiri, args)
      serverlist = nigiri.servers
    for server in serverlist:
      nigiri.channels[server] = map(str, nigiri.proxy.channels(server))
    print "You are on the following channels"
    for server in serverlist:
      print " [%s]" % server
      for channel in nigiri.channels[server]:
        print "  %s" % channel
  return True



def nicks(nigiri, args):
  """irc-call: /nicks [channel]
dbus method: nicks(server, channel)
if no channel is provided, the client will show the nicknames of the current channel"""
  if help_request_p(args):
    print nicks.__doc__
  else:
    # TODO nicklist-stuff
    if len(args) == 0:
      nigiri.proxy.nicks(nigiri.current_server, nigiri.current_channel)
    else:
      nigiri.proxy.nicks(nigiri.current_server, args)
  return True
      



def quit(nigiri, args):
  """irc-call: /quit [message]
dbus method: quit(server, message)
message ist optional und kann leer ("") sein."""
  if help_request_p(args):
    print quit.__doc__
  else:
    nigiri.proxy.quit(nigiri.current_server, args)
  return True



def connect(nigiri, args):
  """irc-call: /connect <server>
dbus method: connect(server)"""
  if help_request_p(args):
    print connect.__doc__
  else:
    nigiri.proxy.connect(args)
    # TODO open new status-tab or something like that
  return True



# Generic

def join(nigiri, args):
  """irc-call: /join <channel>[,<channels>] [key]
dbus method: join(server, channel, key)"
key ist optional und kann leer ("") sein."""
  if help_request_p(args):
    print join.__doc__
  else:
    args = split_first_word(args)
    channels = args[0].split(",")
    key = args[1]
    for channel in channels:
      nigiri.proxy.join(nigiri.current_server, channel, key)
    if len(channels) == 1:
      # TODO set active channel to channels[0]
      pass
    else:
      # stay where you are
      pass
  return True



def part(nigiri, args):
  """irc-call: /part <channel>[,<channels>][ <message>]
dbus method: part(server, channel, message)
message ist optional und kann leer ("") sein."""
  if help_request_p(args):
    print part.__doc__
  else:
    if len(args) == 0:
      nigiri.proxy.part(nigiri.current_server, nigiri.current_channel, "")
      nigiri.channels[nigiri.current_server].remove(nigiri.current_channel)
    else:
      args = split_first_word(args)
      nigiri.proxy.part(nigiri.current_server, args[0], args[1])
  return True



def nick(nigiri, args):
  """irc-call: /nick <new_nick>
dubs method: nick(server, nick)"""
  if help_request_p(args):
    print nick.__doc__
  else:
    if len(args) > 0:
      nigiri.proxy.nick(nigiri.current_server, args)
    own_nick(nigiri, "")
  return True



def own_nick(nigiri, args):
  "dbus method: own_nick(server)"
  if help_request_p(args):
    print own_nick.__doc__
  else:
    nigiri.own_nicks[nigiri.current_server] = nigiri.proxy.own_nick(nigiri.current_server)
  return True



def raw(nigiri, args):
  """irc-call: /raw <command>
dbus method: raw(server, command)"""
  if help_request_p(args):
    print raw.__doc__
  else:
    nigiri.proxy.raw(nigiri.current_server, args)
  return True



# TODO global away to change status on every connected server
def away(nigiri, args):
  """irc-call: /away [<reason>]
dbus method: away(server, message)"""
  if help_request_p(args):
    print away.__doc__
  else:
    nigiri.proxy.away(nigiri.current_server, args)
  return True



# TODO global back to change status on every connected server
def back(nigiri, args):
  """irc-call: /back
dbus method: back(server)"""
  if help_request_p(args):
    print back.__doc__
  else:
    nigiri.proxy.back(nigiri.current_server)
  return True



# Chatting

def message(nigiri, args, current=False):
  """irc-call: /message <target> <message>
          /msg <target> <message>
dbus method: message(server, channel, message)"""
  if help_request_p(args):
    print message.__doc__
  else:
    if current:
      if args:
        nigiri.proxy.message(nigiri.current_server, nigiri.current_channel, args)
    else:
      args = split_first_word(args)
      if args[0] and args[1]:
        nigiri.proxy.message(nigiri.current_server, args[0], args[1])
  return True


def action(nigiri, args):
  """irc-call: /action <message>
          /me <message>
dbus method: action(server, channel, message)"""
  if help_request_p(args):
    print action.__doc__
  else:
    nigiri.proxy.action(nigiri.current_server, nigiri.current_channel, args)
  return True



def notice(nigiri, args):
  """irc-call: /notice <target> <message>
dbus method: notice(server, target, message)"""
  if help_request_p(args):
    print notice.__doc__
  else:
    args = split_first_word(args)
    nigiri.proxy.notice(nigiri.current_server, args[0], args[1])
  return True


# TODO
def ctcp(nigiri, args):
  "dbus method: ctcp(server, target, message)"
  if help_request_p(args):
    print ctcp.__doc__
  else:
    pass
  return True



# Administrative

def shutdown(nigiri, args):
  """irc-call: /shutdown [message]
dbus method: shutdown(message)
message ist optional und kann leer ("") sein."""
  if help_request_p(args):
    print shutdown.__doc__
  else:
    nigiri.proxy.shutdown(args)
  return True



def mode(nigiri, args):
  """irc-call: /mode <own_nick>|<channel> [<mode>[ <parameters>]]
example: /mode #channel +o own_nick
dbus method: mode(server, target, mode)"""
  if help_request_p(args):
    print mode.__doc__
  else:
    args = split_first_word(args)
    nigiri.proxy.mode(nigiri.current_server, args[0], args[1])
  return True



def kick(nigiri, args):
  """irc-call: /kick <who> <message>
dbus method: kick(server, channel, who, message)
message ist optional und kann leer ("") sein."""
  if help_request_p(args):
    print kick.__doc__
  else:
    args = split_first_word(args)
    nigiri.proxy.kick(nigiri.current_server, nigiri.current_channel, args[0], args[1])
  return True



def topic(nigiri, args):
  """irc-call: /topic <topic>"
dbus method: topic(server, channel, topic)"""
  if help_request_p(args):
    print topic.__doc__
  else:
    nigiri.proxy.topic(nigiri.current_server, nigiri.current_channel, args)
  return True



# Config

def sushi_get(nigiri, args):
  "dbus method: sushi_get(file, group, key)"
  if help_request_p(args):
    print sushi_get.__doc__
  else:
    pass
  return True



def sushi_set(nigiri, args):
  "dbus method: sushi_set(file, group, key, value)"
  if help_request_p(args):
    print sushi_set.__doc__
  else:
    pass
  return True



def sushi_remove(nigiri, args):
  """dbus method: sushi_remove(file, group, key)
key ist optional und kann leer ("") sein. Dann wird die ganze Gruppe entfernt.
group ist optional und kann leer ("") sein. Dann wird die ganze Datei entfernt."""
  if help_request_p(args):
    print sushi_remove.__doc__
  else:
    pass
  return True



def sushi_list(nigiri, args):
  """dbus method: sushi_list(directory, file, group)
group ist optional und kann leer ("") sein. Dann werden alle Gruppen aufgelistet.
file ist optional und kann leer ("") sein. Dann werden alle Dateien aufgelistet."""
  if help_request_p(args):
    print sushi_list.__doc__
  else:
    pass
  return True




###
# Input Handler
###

def get_commandlist():
  return { 'join': join,
           'message': message,
           'part': part,
           'quit': quit,
           'kick': kick,
           'nick': nick,
           'connect': connect,
           'action': action,
           'me': action,
           'away': away,
           'back': back,
           'shutdown': shutdown,
           'ctcp': ctcp,
           'notice': notice,
           'mode': mode,
           'servers': servers,
           'channels': channels,
           'nicks': nicks,
           'quit': quit,
           'connect': connect,
           'join': join,
           'part': part,
           'nick': nick,
           'own_nick': own_nick,
           'raw': raw,
           'away': away,
           'back': back,
           'message': message,
           'msg': message,
           'action': action,
           'ctcp': ctcp,
           'notice': notice,
           'shutdown': shutdown,
           'mode': mode,
           'kick': kick,
           'topic': topic,
           'sushi_get': sushi_get,
           'sushi_set': sushi_set,
           'sushi_remove': sushi_remove,
           'sushi_list': sushi_list
         }


def help_request_p(arg):
  "checks if the given argument is a request for help"
  return arg in ['--help', '-h', '-?', '/?']



def split_first_word(message, separator = None):
  "splits the first word, delimited by separator, and returns a list where [0] is the word and [1] the rest of the string"
  strings = message.split(separator, 1)

  for i in range(2 - len(strings)):
    strings.append("")

  return strings



def input_handler(inputstream, io_condition, nigiri):
  input = inputstream.readline().rstrip("\r\n")

  if len(input) == 0:
    return True

  if input[0] != "/":
    return message(nigiri, input, current=True)

  if input == "/exit":
    nigiri.loop.quit()
    return False

  if len(input) == 1:
    return True

  if input[0] == "/":
    if input[1] == "/":
      return message(nigiri, input[1:], current=True)

    input = split_first_word(input[1:])

    try:
      ret = nigiri.commandlist[input[0]](nigiri, input[1])
    except KeyError:
      print "Unknown command: %s" % (input[0])
      ret = True

    return ret
