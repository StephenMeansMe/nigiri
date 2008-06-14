include ../Makefile.common

all:

install: all
	$(INSTALL) -d -m 755 '$(sharedir)/sushi/nigiri'
	$(INSTALL) -m 644 *.py '$(sharedir)/sushi/nigiri'
	$(CHMOD) +x '$(sharedir)/sushi/nigiri/nigiri.py'
	$(LN) '$(sharedir)/sushi/nigiri/nigiri.py' '$(bindir)/nigiri'

clean:
	$(RM) *.pyc
