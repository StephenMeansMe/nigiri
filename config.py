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

from xdg.BaseDirectory import xdg_config_home, xdg_data_home, xdg_cache_home
import ConfigParser

from typecheck import types
from messages import print_debug
from helper.escape import unescape_split, escape_join

prefix = ""
defaults = {}

config_parser = None
config_file = ""

def get_path(*c):
	return os.path.abspath(os.path.join(prefix, *c))

def set_defaults():
	"""
		Sets the default values.

		I know that the ConfigParser class has a
		method to set defaults but these defaults
		are global and not bound to a section.
		If you want a default nick color you can
		set it but if you have another option
		with the same name the default value will
		be the same and this sucks.

		A further point is that this way realizes
		"private" values which are not written
		to config files but can be used with the same
		API.
	"""
	global defaults

	defaults = {}
	defaults["aliase"] = {}

	defaults["nigiri"] = {}
	defaults["nigiri"]["wrap_input"] = "True"
	defaults["nigiri"]["command_char"] = "/"
	defaults["nigiri"]["shortcut_pattern"] = "meta [0-9]"
	defaults["nigiri"]["server_shortcuts"] = "true"
	defaults["nigiri"]["show_debug"] = "True"
	defaults["nigiri"]["logfile"] = os.path.join(xdg_cache_home, "sushi", "nigiri.txt")
	defaults["nigiri"]["locale_dir"] = get_path("..", "locale")
	defaults["nigiri"]["plugin_dirs"] = escape_join(",", (
			os.path.join(xdg_data_home, "nigiri", "plugins"),
			os.path.join(xdg_data_home, "chirashi"),
			get_path("plugins"),
			get_path("..", "chirashi")
		))

	defaults["chatting"] = {}
	defaults["chatting"]["quit_message"] = "Quit."
	defaults["chatting"]["part_message"] = "Part."
	defaults["chatting"]["last_log_lines"] = "15"
	defaults["chatting"]["nick_separator"] = ": "

	defaults["colors"] = {}
	defaults["colors"]["messages"] = "gray"
	defaults["colors"]["messages_own"] = "white"
	defaults["colors"]["messages_highlight"] = "red"
	defaults["colors"]["actions"] = "gray"
	defaults["colors"]["actions_own"] = "white"
	defaults["colors"]["informative"] = "blue"

	defaults["templates"] = {}
	# misc
	defaults["templates"]["datestring"] = "%H:%M"
	# messages
	defaults["templates"]["action"] = "%(time)s %(nick)s %(message)s"
	defaults["templates"]["action_own"] = "%(time)s %(nick)s %(message)s"
	defaults["templates"]["message"] = "%(time)s <%(prefix)s%(nick)s> %(message)s"
	defaults["templates"]["message_own"] = "%(time)s <%(prefix)s%(nick)s> %(message)s"
	defaults["templates"]["ctcp"] = "%(time)s -%(nick)s/%(target)s- %(message)s"
	defaults["templates"]["ctcp_own"] = "%(time)s -%(nick)s/%(target)s- %(message)s"
	defaults["templates"]["notice"] = "%(time)s *%(nick)s/%(target)s* %(message)s"
	defaults["templates"]["notice_own"] = "%(time)s *%(nick)s/%(target)s* %(message)s"

	# actions
	defaults["templates"]["invite"] = "%(time)s * %(nick)s invites %(who)s to %(channel)s"
	defaults["templates"]["invite_own"] = "%(time)s * You were invited by %(nick)s to %(channel)s."
	defaults["templates"]["join"] = "%(time)s * %(nick)s (%(host)s) has joined %(channel)s."
	defaults["templates"]["join_own"] = "%(time)s * You have joined %(channel)s."
	defaults["templates"]["kick"] = "%(time)s * %(who)s got kicked from %(channel)s by %(nick)s (%(reason)s)"
	defaults["templates"]["kick_own"] = "%(time)s * You got kicked from %(channel)s by %(nick)s (%(reason)s)"
	defaults["templates"]["nick"] = "%(time)s * %(nick)s is now known as %(new_nick)s."
	defaults["templates"]["nick_own"] = "%(time)s * You are now known as %(new_nick)s."
	defaults["templates"]["mode_list"] = "%(time)s * Modes for %(target)s: %(modes)s."
	defaults["templates"]["mode_list_own"] = "%(time)s * Modes set on you: %(modes)s."
	defaults["templates"]["mode"] = "%(time)s %(nick)s set %(mode)s%(param)s on %(target)s."
	defaults["templates"]["mode_own"] = "%(time)s You set %(mode)s%(param)s on %(target)s."
	defaults["templates"]["oper"] = "%(time)s * %(nick)s is now an OPER."
	defaults["templates"]["oper_own"] = "%(time)s * You are now an OPER."
	defaults["templates"]["part"] = "%(time)s * %(nick)s has left %(channel)s (%(reason)s)."
	defaults["templates"]["part_own"] = "%(time)s * You have left %(channel)s (%(reason)s)."
	defaults["templates"]["quit"] = "%(time)s * %(nick)s has quit (%(reason)s)."
	defaults["templates"]["quit_own"] = "%(time)s * You have quit (%(reason)s)."
	defaults["templates"]["topic"] = "%(time)s * %(nick)s has set the topic on %(channel)s to \"%(topic)s\"."
	defaults["templates"]["topic_own"] = "%(time)s * You have set the topic on %(channel)s to \"%(topic)s\"."
	defaults["templates"]["topic_anonymous"] = "* Topic of %(channel)s: %(topic)s"

	# informative
	defaults["templates"]["banlist_begin"] = "%(time)s Begin of banlist on channel %(channel)s."
	defaults["templates"]["banlist_item"] = ">> %(who)s %(mask)s %(when)s"
	defaults["templates"]["banlist_end"] = "%(time)s End of banlist. (%(channel)s)"
	defaults["templates"]["cannot_join"] = "%(time)s Can't join channel %(channel)s: %(reason)s"
	defaults["templates"]["list_begin"] = "%(time)s Begin of list."
	defaults["templates"]["list_item"] = ">> %(channel)s %(user)s %(topic)s"
	defaults["templates"]["list_end"] = "%(time)s End of list."
	defaults["templates"]["names_begin"] = "%(time)s Begin of names (%(channel)s)."
	defaults["templates"]["names_item"] = "[ %(row)s ]"
	defaults["templates"]["names_end"] = "%(time)s End of names."
	defaults["templates"]["no_such"] = "%(time)s No such %(type)s: %(target)s."
	defaults["templates"]["whois_begin"] = "%(time)s Begin of whois (%(target)s)."
	defaults["templates"]["whois_item"] = ">> %(nick)s: %(message)s"
	defaults["templates"]["whois_end"] = "%(time)s End of whois."
	defaults["templates"]["dcc_new_incoming"] = "%(time)s Incoming file transfer (ID:%(id)d) from %(sender)s: \"%(filename)s\" (%(size)d)."
	defaults["templates"]["dcc_file_auto_accept"] = "%(time)s Auto accepted file transfer from %(sender)s: \"%(filename)s\" (%(size)d)."

	# Add default sections to config parser
	# so setting is easier
	for section in defaults.keys():
		try:
			config_parser.add_section(section)
		except ConfigParser.DuplicateSectionError:
			continue

	# sections defined below are not added to the configParser and
	# can't be set by the set method (will raise NoSectionError)
	pass

@types (name=str, address=str, port=int, user=str, password=str, log=bool)
def read_config_file():
	"""
	Reads the config file.
	"""
	success = config_parser.read([config_file])

	if not success:
		print "Failed to parse config file '%s'" % config_file
		return False

	return True

def write_config_file():
	"""
	Writes the config values from the
	ConfigParser object into the given file (config_file)
	"""
	if not config_parser:
		print "Config module not loaded. I don't save anything."
		return

	f = file(config_file, "w")
	config_parser.write(f)
	f.close()

@types (section=basestring)
def create_section(section):
	"""
		creates config section `section`.
	"""
	if not config_parser or config_parser.has_section(section):
		return False
	config_parser.add_section(section)
	return True

@types (section=basestring)
def remove_section(section):
	"""
		removes the section
	"""
	if not config_parser or not config_parser.has_section(section):
		return False

	config_parser.remove_section(section)
	return True

@types (section=basestring, option=basestring)
#@on_fail (print_debug, "ConfigError while setting %s:%s to %s")
def set(section, option, value):
	"""
		Sets in the section the option to value.
		On success the method returns True.
	"""
	if not config_parser:
		return False

	try:
		config_parser.set(section, option, str(value))
	except ConfigParser.NoSectionError:
		return False
	else:
		return True

@types (section=basestring, option=basestring, l=list)
def set_list(section, option, l):
	"""
	join the list l to a string separated
	by , and set it as value to option.
	Return False on error, else True.
	"""
	s = escape_join(",", l)

	if None == s:
		return False

	return set(section, option, s)

@types (section=basestring, option=basestring, value=basestring)
def append_list(section, option, value):
	"""
	add value to the list identified by option
	"""
	v = get_list(section, option, [])
	v.append(value)
	return set_list(section, option, v)

@types (section=basestring, option=basestring)
def unset(section, option):
	"""
		Removes the option in the section.
		Returns True on success otherwise False.
	"""
	if not config_parser:
		return False
	try:
		config_parser.remove_option(section, option)
	except ConfigParser.NoSectionError,e:
		print "Unsetting ('%s','%s') failed: %s" % (section,option,e)
		return False
	return True

@types (section=basestring, option=basestring)
def get(section, option="", default=None):
	"""
		Returns the value for option in section, on
		error the method returns default.

		If option is not given, the whole section
		is returned as dictionary of type {option:value}.
		If there are default values for the section they
		will be merged in.

		The `option`-value is handled case-insensitive.

		get("tekka") will return {"server_shortcuts":"1"}
		get("tekka","server_shortcuts") will return "1"
		get("tekki") will return default
	"""

	if not config_parser:
		return default

	if not option:
		# get the whole section

		if config_parser.has_section(section):
			# the section is noticed by the parser,
			# merge with defaults (if any) and return
			# the value-dict

			new = dict(config_parser.items(section))

			if defaults.has_key(section):
				# merge defaults + config values together
				copy = defaults[section].copy()
				copy.update(new)
				return copy
			else:
				return new

		elif defaults.has_key(section):
			# the config parser does not know the
			# section but it's found in defaults-dict.
			# This is probably a private section.
			return defaults[section]

		else:
			return default

	else:
		# get specific option

		try:
			return config_parser.get(section, option)
		except (ConfigParser.NoOptionError, ConfigParser.NoSectionError),e:
			if defaults.has_key(section):
				try:
					return defaults[section][option]
				except KeyError:
					return default
		else:
			return default

	# usually this is not reached
	return default

@types (section=basestring, option=basestring)
def get_list(section, option, default):
	"""
		Splits the option in the section for ","
		and returns a list if the splitting was
		successful. Else the method will return
		"default".
	"""
	res = get(section, option, default)

	if res == default:
		return default

	l = unescape_split(",", res)

	if not l:
		return default
	return list(l)

@types (section=basestring, option=basestring)
def get_bool(section, option, default=False):
	"""
		Returns True or False if the value is
		set or unset.
	"""
	res = get(section, option, default)

	if res == default:
		return default

	if res.lower() == "true" or res == "1":
		return True

	return default

@types (section=basestring, option=basestring)
def get_default(section, option=""):
	"""
	Returns the default value for the option
	in the given section. If no option is given
	(option = None) all defaults of the given
	section are returned as a dictionary.
	If there are no defaults, None is returned.
	"""
	if not option:
		if defaults.has_key(section):
			return defaults[section]
	else:
		if defaults.has_key(section):
			if defaults[section].has_key(option):
				return defaults[section][option]
	return None

@types (path=basestring)
def check_config_file(path):
	""" check if config file exists and create it if not """
	if not os.path.exists (path):
		# create the directories
		try:
			os.makedirs (os.path.join (os.path.split (path)[0]))
		except os.error:
			print "Error while creating neccessary directories: %s"\
				% (os.error)
			return False

		try:
			f = file (path, "w")
		except BaseException,e:
			print "Error while creating config file: %s" % (e)
			return False
		else:
			f.close()

		return True
	else:
		return True
	return False

def setup():
	"""
	Find the usual location of the config dir
	(XDG_CONFIG_HOME/sushi) and parse the
	config file (nigiri) if found.
	"""
	global config_parser, config_file
	global prefix

	if os.path.islink(sys.argv[0]):
		link = os.readlink(sys.argv[0])

		if not os.path.isabs(link):
			link = os.path.join(os.path.dirname(sys.argv[0]), link)

		prefix = os.path.dirname(os.path.abspath(link))
	else:
		prefix = os.path.dirname(os.path.abspath(sys.argv[0]))

	config_parser = ConfigParser.ConfigParser()
	set_defaults()

	config_file = os.path.join (xdg_config_home, "sushi", "nigiri")

	if not check_config_file(config_file):
		print "Config file creation failed. Aborting."
		return

	read_config_file()

