############################################
##  Licence: Public Domain
############################################

###
# DBus Methods
###

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
    args = args.split(" ")
    channels = args[0].split(",")
    key = ""
    if len(args) == 2:
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
      args = args.split(" ")
      nigiri.proxy.part(nigiri.current_server, args[0], args[1])
  return True



def nick(nigiri, args):
  "dubs method: nick(server, nick)"
  if help_request_p(args):
    print nick.__doc__
  else:
    pass
  return True



def own_nick(nigiri, args):
  "dbus method: own_nick(server)"
  if help_request_p(args):
    print own_nick.__doc__
  else:
    pass
  return True



def raw(nigiri, args):
  "dbus method: raw(server, command)"
  if help_request_p(args):
    print raw.__doc__
  else:
    pass
  return True



def away(nigiri, args):
  "dbus method: away(server, message)"
  if help_request_p(args):
    print away.__doc__
  else:
    pass
  return True



def back(nigiri, args):
  "dbus method: back(server)"
  if help_request_p(args):
    print back.__doc__
  else:
    pass
  return True



# Chatting

def message(nigiri, args, current_target):
  "dbus method: message(server, channel, message)"
  if help_request_p(args):
    print message.__doc__
  else:
    pass
  return True



def action(nigiri, args):
  "dbus method: action(server, channel, message)"
  if help_request_p(args):
    print action.__doc__
  else:
    pass
  return True



def ctcp(nigiri, args):
  "dbus method: ctcp(server, target, message)"
  if help_request_p(args):
    print ctcp.__doc__
  else:
    pass
  return True



def notice(nigiri, args):
  "dbus method: notice(server, target, message)"
  if help_request_p(args):
    print notice.__doc__
  else:
    pass
  return True



# Administrative

def shutdown(nigiri, args):
  "dbus method: shutdown()"
  if help_request_p(args):
    print shutdown.__doc__
  else:
    pass
  return True



def mode(nigiri, args):
  "dbus method: mode(server, target, mode)"
  if help_request_p(args):
    print mode.__doc__
  else:
    pass
  return True



def kick(nigiri, args):
  """dbus method: kick(server, channel, who, message)
message ist optional und kann leer ("") sein."""
  if help_request_p(args):
    print kick.__doc__
  else:
    pass
  return True



def topic(nigiri, args):
  "dbus method: topic(server, channel, topic)"
  if help_request_p(args):
    print topic.__doc__
  else:
    pass
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
  return arg in ['--help', '-h', '-?', '/?']



def input_handler(inputstream, io_condition, nigiri):
  input = inputstream.readline()
  if input[0] != "/":
    return message(nigiri, input, current_target=True)
  if input == "/exit\n":
    nigiri.loop.quit()
    return False
  if input[0] == "/":
    input = input[1:-1]
    space = input.find(" ")
    if space == -1:
      space = len(input)
    command = input[:space]
    args = input[space + 1:]
    try:
      ret = nigiri.commandlist[command](nigiri, args)
    except KeyError:
      ret = True
    return ret
