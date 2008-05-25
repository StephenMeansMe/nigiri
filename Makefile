include ../Makefile.common

all:

install: all
	$(INSTALL) -d -m 755 '$(PREFIX)/share/nigiri'
	$(INSTALL) -m 755 *.py '$(PREFIX)/share/nigiri'
	$(LN) '../share/nigiri/nigiri.py' '$(PREFIX)/bin/nigiri'

clean:
	$(RM) *.pyc
