include ../Makefile.common

all:

install: all
	$(INSTALL) -d -m 755 '$(DESTDIR)$(bindir)'
	$(INSTALL) -d -m 755 '$(DESTDIR)$(sharedir)/sushi/nigiri'
	$(INSTALL) -d -m 755 '$(DESTDIR)$(sharedir)/sushi/nigiri/extends'
	$(INSTALL) -d -m 755 '$(DESTDIR)$(sharedir)/sushi/nigiri/helper'
	$(INSTALL) -d -m 755 '$(DESTDIR)$(mandir)/man1'
	$(INSTALL) -m 644 *.py '$(DESTDIR)$(sharedir)/sushi/nigiri'
	$(INSTALL) -m 644 extends/*.py '$(DESTDIR)$(sharedir)/sushi/nigiri/extends'
	$(INSTALL) -m 644 helper/*.py '$(DESTDIR)$(sharedir)/sushi/nigiri/helper'
	# FIXME
	$(SED) 's#@SUSHI_VERSION@#$(SUSHI_VERSION)#' 'main.py' > '$(DESTDIR)$(sharedir)/sushi/nigiri/main.py'
	$(CHMOD) +x '$(DESTDIR)$(sharedir)/sushi/nigiri/main.py'
	$(LN) -sf '$(sharedir)/sushi/nigiri/main.py' '$(DESTDIR)$(bindir)/nigiri'
	$(SED) 's#@SUSHI_VERSION@#$(SUSHI_VERSION)#' 'nigiri.1.in' | $(GZIP) > '$(DESTDIR)$(mandir)/man1/nigiri.1.gz'

	$(MAKE) -C po $@

clean:
	$(MAKE) -C po $@

	$(RM) -f *.pyc
	$(RM) -f helper/*.pyc
	$(RM) -f extends/*.pyc
