include ../Makefile.common

all:

install: all
#	$(INSTALL) -d -m 755 '$(DESTDIR)$(bindir)'
#	$(INSTALL) -d -m 755 '$(DESTDIR)$(sharedir)/sushi/nigiri'
#	$(INSTALL) -m 644 *.py '$(DESTDIR)$(sharedir)/sushi/nigiri'
#	$(CHMOD) +x '$(DESTDIR)$(sharedir)/sushi/nigiri/nigiri.py'
#	$(LN) -sf '$(sharedir)/sushi/nigiri/nigiri.py' '$(DESTDIR)$(bindir)/nigiri'

clean:
	$(RM) -f *.pyc
