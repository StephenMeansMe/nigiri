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

import commands
import config
import tabs

# types identificating the current scroll position
(
	NO_TYPE,
	NICK_TYPE,
	QUERY_TYPE,
	CHANNEL_TYPE,
	COMMAND_TYPE
) = range(5)

# cache of position
_current = {
	"position": None,
	"tab": None,
	"type": NO_TYPE,
	"needle": None,
	"lastCompletion": None
}

# reference to the main window
_main_window = None

def _reset_iteration():
	global _current
	_current["position"] = None
	_current["tab"] = None
	_current["type"] = NO_TYPE
	_current["needle"] = None
	_current["lastCompletion"] = None

def _appendMatch(entry, text, word, match, separator=" "):
	""" Complete `word` in `text` with `match` and
		apply it to the input bar widget.
		Add separator too.
	"""
	# old text without needle + new_word + separator + rest
	new_text = text[0:entry.edit_pos-len(word)] + \
		match + \
		separator + \
		text[entry.edit_pos:]

	old_position = entry.edit_pos
	entry.set_edit_text(new_text)

	entry.set_edit_pos(old_position + len(match+separator) -len(word))

	global _current
	_current["lastCompletion"] = match + separator

def _removeLastCompletion(entry, text):
	""" this function assumes, we're on the position _after_
		the completion...
	"""
	lc = _current["lastCompletion"]

	if lc == None:
		return text

	# strip of the match, keep the needle:
	# 'n'<Tab> => 'nemo: ' => strip 'emo: '
	needle = _current["needle"]
	skip = (entry.edit_pos - len(lc)) + len(needle)
	new_text = text[:skip]+text[entry.edit_pos:]

	entry.set_edit_text(new_text)
	entry.set_edit_pos(skip)

	return new_text

def _raise_position(matches, i_type):
	if _current["type"] == i_type:
		# continue iterating
		if (_current["position"]+1 >= len(matches)
			or _current["position"] == None):
			_current["position"] = 0

		else:
			_current["position"] += 1

	else:
		# set type to the current and begin iterating
		_current["type"] = i_type
		_current["position"] = 0

def _match_nick_in_channel(tab, word):
	matches = [n for n in tab.nicklist.keys() if n[:len(word)].lower() == word.lower()]
	# sort nicks alphabetically
	matches.sort(lambda x, y: cmp(x.lower(), y.lower()))

	if matches:
		_raise_position(matches, NICK_TYPE)
		return matches[_current["position"]]
	return None

def _match_nick_in_query(tab, word):
	matches = [nick for nick in (tab.name, (tab.is_server() and tab.nick or tab.parent.nick)) if nick[:len(word)].lower() == word.lower()]

	if matches:
		_raise_position(matches, QUERY_TYPE)
		return matches[_current["position"]]
	return None

def _match_channel(word):
	global _main_window

	tablist = tabs.tree_to_list(_main_window.servers)

	# find all matching tabs
	matches = [tab.name for tab in tablist
		if tab and tab.name[:len(word)].lower() == word.lower()]

	if matches:
		_raise_position(matches, CHANNEL_TYPE)
		return matches[_current["position"]]
	return None

def _match_command(word):
	matches = [cmd for cmd in commands._command_dict.keys()
	if cmd[:len(word)].lower()==word.lower()]

	if matches:
		_raise_position(matches, COMMAND_TYPE)
		return matches[_current["position"]]
	return None

def stopIteration():
	""" user does not want any more results, stop the iteration.
		This is the case if, for example, the tab is switched or
		the input bar is activated.
	"""
	_reset_iteration()

def setup(main_window):
	global _main_window
	_main_window = main_window

def complete(entry, text):
	""" search for the last typed word and try to
		complete it in the following order:
		- search for a suitable nick in the channel (if tab is a channel)
		- search for a suitable nick in the query (if tab is a query)
		- search for a suitable command (if the first letter is a '/')
		- search for a suitable channel (if the first letter is
		  a valid channel prefix)

		If one of the searches matches, this function returns True.
		If no search matches, False is returned.

		The function checks, if the word searched for was the
		same as last time. So if complete is called another
		time, it will continue searching and using the next
		result to the one before.
	"""

	global _current

	currentTab = _main_window.current_tab

	if not text:
		return False

	if currentTab != _current["tab"]:
		# reset iteration, data is not up to date.
		# start new iteration, then
		_reset_iteration()
		_current["tab"] = currentTab

	if _current["needle"]:
		# continue searching for `needle`
		word = _current["needle"]
		text = _removeLastCompletion(entry, text)

	else:
		# get the word to complete
		# "f|<tab> || f |<tab>"
		word = text[0:entry.edit_pos].split(" ")[-1].strip()

		_current["needle"] = word

	if not word:
		return False

	match = None

	if currentTab and type(currentTab) == tabs.Channel:
		# look for nicks

		match = _match_nick_in_channel(currentTab, word)

		if match:

			# if the word is in a sentence, use command
			# completion (only whitespace)
			if text.count(" ") < 1:
				separator = config.get("chatting", "nick_separator")
			else:
				separator = " "

			_appendMatch(entry, text, word, match,
				separator = separator)

			return True

	elif currentTab and type(currentTab) == tabs.Query:
		# look for my nick or the other nick

		match = _match_nick_in_query(currentTab, word)

		if match:
			if text.count(" ") < 1:
				separator = config.get("chatting", "nick_separator")
			else:
				separator = " "

			_appendMatch(entry, text, word, match,
				separator = separator)

			return True

	# ** no successful completion so far **

	# channel completion
	if (currentTab
	and word[0] in (type(currentTab) == tabs.Server
					and currentTab.support_chantypes
					or currentTab.parent.support_chantypes)):

		match = _match_channel(word)

		if match:
			_appendMatch(entry, text, word, match)
			return True

	# *** command completion ***

	if word[0] == "/":

		match = _match_command(word[1:])

		if match:
			_appendMatch(entry, text, word, "/"+match)
			return True

	return False
