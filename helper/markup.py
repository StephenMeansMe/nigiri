

def get_occurances(haystack,needle,l=[],start=0,end=-1):
	""" return a list with all indices of needle in haystack """
	i = haystack.find(needle,start)
	if i == -1: return l
	return get_occurances(haystack,needle,l+[i],i+1)

def tuple_to_list(t):
	""" Convert a markup tuple:
			(text,[(color,pos),...])
		To a markup list:
			[(color,textpart),...]
		This is the opposite to urwid.util.decompose_tagmarkup
	"""
	(text,attrs) = t
	pc = 0
	l = []

	for (attr,pos) in attrs:
		if attr == None:
			l.append(text[pc:pc+pos])

		else:
			l.append((attr, text[pc:pc+pos]))
		pc += pos

	return l


def colorize_mult(text, needles, colors, base_color="default"):
	""" colorize more than one needle with a color.
		If base_color is given, the text not matching a needle
		is colored with the base_color.

		Example: colorize_mult("foo bar baz",["foo","baz"],
			{"foo":"green","baz":"blue"}) ->
			[("green","foo")," bar ",("blue","baz")]

				colorize_mult("foo bar baz",["foo","baz"],
			{"foo":"green","baz":"blue"}, base_color="red") ->
			[("green","foo"),("red"," bar "),("blue","baz")]
		Returns a markup list.
	"""
	# list sorted descending by needle length
	needles = sorted(needles, cmp=lambda a,b: (
		(len(a)>len(b) and -1) or (len(a)<len(b) and 1) or 0))

	def join(l,elem):
		nl = []
		for i in l[:-1]:
			if i != '':
				nl.append(i)
			nl.append(elem)
		if l and l[-1] != '':
			nl.append(l[-1])
		return nl

	l = [text]
	for needle in needles:
		nl = []
		for i in l:
			if isinstance(i,basestring):
				split = i.split(needle)
				if len(split) > 1:
					x = join(split,(colors[needle],needle))
					nl = nl + x
				else:
					nl.append(i)
			else:
				nl.append(i)
		l = nl

	if base_color != "default":
		nl = []
		for i in l:
			if isinstance(i,basestring):
				nl.append((base_color,i))
			else:
				nl.append(i)
		l = nl

	return l

def colorize(text, needle, color, base_color, start=0, end=-1):
	""" Color all occurances of needle in text in the given
		color. The markup will have the tuple-form like:
			(thetext,[(attr1,pos),...])
	"""
	occ = get_occurances(text,needle,start=start,end=end)
	p = 0
	l = []

	for i in occ:
		if i != p:
			if i-p > 0:
				l.append((base_color,i-p))
		l.append((color,len(needle)))
		p = i
	rest = len(text)-(p+len(needle))
	if rest > 0:
		l.append((base_color,rest))

	return (text, l)


if __name__ == "__main__":

	print "Testing tuple_to_list."

	r = tuple_to_list(("foobarbaz",[("red",3),("green",3),("blue",3)]))
	assert r == [("red","foo"),("green","bar"),("blue","baz")]

	r = tuple_to_list(("foobarbaz",[("red",3),(None,3),("blue",3)]))
	assert r == [("red","foo"),"bar",("blue","baz")]

	print "Success."

	print "Testing get_occurances."
	assert [0,1,2,3] == get_occurances("aaaa","a")
	assert [3] == get_occurances("abcde","d")
	assert [] == get_occurances("foo","x")
	print "Success."

	print "Testing colorize."
	text = "00:11 <nick> Das ist ein Test."
	color = "green"
	nick = "nick"
	base_color = "default"

	assert (text,[("default",7),("green",4),("default",19)]) == colorize(
		text,nick,color,base_color)
	print "Success."

	print "Testing colorize_mult."
	assert colorize_mult("foo bar baz",["foo","baz"],
			{"foo":"green","baz":"blue"}) == [
			("green","foo")," bar ",("blue","baz")]
	assert colorize_mult("foo bar baz",["foo","baz"],
			{"foo":"green","baz":"blue"}, base_color="red") == [
			("green","foo"),("red"," bar "),("blue","baz")]
	print "Success."
