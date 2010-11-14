#!/usr/bin/env python

from waflib import Utils

APPNAME = 'nigiri'
VERSION = '1.4.0'

top = '.'
out = 'build'

def configure (ctx):
	ctx.load('gnu_dirs')

	ctx.find_program('gzip', var = 'GZIP')

	ctx.env.VERSION = VERSION

	ctx.recurse('po')

def build (ctx):
	ctx.install_files('${DATAROOTDIR}/sushi/nigiri', ctx.path.ant_glob('*.py'))
	ctx.install_files('${DATAROOTDIR}/sushi/nigiri/extends', ctx.path.ant_glob('extends/*.py'))
	ctx.install_files('${DATAROOTDIR}/sushi/nigiri/helper', ctx.path.ant_glob('helper/*.py'))
	ctx.install_files('${DATAROOTDIR}/sushi/nigiri/plugins', ctx.path.ant_glob('plugins/*.py'))

	ctx.symlink_as('${BINDIR}/nigiri', Utils.subst_vars('${DATAROOTDIR}/sushi/nigiri/main.py', ctx.env))

	# FIXME
	ctx(
		features = 'subst',
		source = 'main.py.in',
		target = 'main.py',
		install_path = '${DATAROOTDIR}/sushi/nigiri',
		chmod = 0755,
		SUSHI_VERSION = ctx.env.VERSION
	)

	for man in ('nigiri.1',):
		ctx(
			features = 'subst',
			source = '%s.in' % (man),
			target = man,
			install_path = None,
			SUSHI_VERSION = ctx.env.VERSION
		)

	ctx.add_group()

	for man in ('nigiri.1',):
		ctx(
			source = man,
			target = '%s.gz' % (man),
			rule = '${GZIP} -c ${SRC} > ${TGT}',
			install_path = '${MANDIR}/man1'
		)

	ctx.recurse('po')
