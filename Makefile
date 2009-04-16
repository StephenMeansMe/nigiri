include ../Makefile.common

all:

install: all
	$(INSTALL) -d -m 755 '$(DESTDIR)$(bindir)'
	$(INSTALL) -d -m 755 '$(DESTDIR)$(sharedir)/sushi/nigiri'
	$(INSTALL) -d -m 755 '$(DESTDIR)$(sharedir)/sushi/nigiri/extends'
	$(INSTALL) -d -m 755 '$(DESTDIR)$(sharedir)/sushi/nigiri/helper'
	$(INSTALL) -d -m 755 '$(DESTDIR)$(sharedir)/sushi/nigiri/plugins'
	$(INSTALL) -m 644 *.py '$(DESTDIR)$(sharedir)/sushi/nigiri'
	$(INSTALL) -m 644 extends/*.py '$(DESTDIR)$(sharedir)/sushi/nigiri/extends'
	$(INSTALL) -m 644 helper/*.py '$(DESTDIR)$(sharedir)/sushi/nigiri/helper'
	$(INSTALL) -m 644 plugins/*.py '$(DESTDIR)$(sharedir)/sushi/nigiri/plugins'
	# FIXME
	$(SED) 's#@SUSHI_VERSION@#$(SUSHI_VERSION)#' 'main.py' > '$(DESTDIR)$(sharedir)/sushi/nigiri/main.py'
	$(CHMOD) +x '$(DESTDIR)$(sharedir)/sushi/nigiri/main.py'
	$(LN) -sf '$(sharedir)/sushi/nigiri/main.py' '$(DESTDIR)$(bindir)/nigiri'

clean:
	$(RM) -f *.pyc
	$(RM) -f helper/*.pyc
	$(RM) -f extends/*.pyc
	$(RM) -f plugins/*.pyc
