include ../../Makefile.common

LANGUAGES =
PO        = $(LANGUAGES:%=%.po)
PY        = $(wildcard ../*.py) $(wildcard ../*/*.py)

all:

install: $(PO:%.po=%.mo)
	for file in $+; do \
		INSTALL='$(INSTALL)' ../../tools/install-mo.sh nigiri "$${file}" '$(DESTDIR)$(localedir)'; \
	done

clean:
	$(RM) -f nigiri.pot
	$(RM) -f *.mo

nigiri.pot: $(PY)
	$(QUIET_GEN) xgettext --keyword=_ --keyword=N_ --output=$@ $+

%.mo: %.po
	$(QUIET_GEN) msgfmt --output-file=$@ $+
