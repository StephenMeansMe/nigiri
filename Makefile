include ../Makefile.common
PREFIX=/usr/share

all:

install: all
	$(INSTALL) -d -m 755 '$(PREFIX)/nigiri'
	$(INSTALL) -m 755 *py '$(PREFIX)/nigiri'
	$(LN) '$(PREFIX)/nigiri/nigiri.py' '/usr/bin/nigiri'

clean:
	$(RM) *.pyc
