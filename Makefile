include ../Makefile.common

all:

install: all
	$(INSTALL) -d -m 755 '$(sharedir)/sushi/nigiri'
	$(INSTALL) -m 755 *.py '$(sharedir)/sushi/nigiri'
	$(LN) '$(sharedir)/sushi/nigiri/nigiri.py' '$(bindir)/nigiri'

clean:
	$(RM) *.pyc
