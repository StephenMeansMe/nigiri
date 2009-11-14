#!/usr/bin/env python

import Utils

APPNAME = 'nigiri'
VERSION = '1.1.0'

srcdir = '.'
blddir = 'build'

def configure (conf):
	conf.check_tool('gnu_dirs')
	conf.check_tool('misc')

	conf.env.VERSION = VERSION

	conf.sub_config('po')

def build (bld):
	bld.add_subdirs('po')

	# FIXME Waf 1.5.9 bug
	bld.new_task_gen()

	bld.install_files('${DATAROOTDIR}/sushi/nigiri', bld.glob('*.py'))
	bld.install_files('${DATAROOTDIR}/sushi/nigiri/extends', bld.glob('extends/*.py'))
	bld.install_files('${DATAROOTDIR}/sushi/nigiri/helper', bld.glob('helper/*.py'))

	bld.symlink_as('${BINDIR}/nigiri', Utils.subst_vars('${DATAROOTDIR}/sushi/nigiri/main.py', bld.env))

	# FIXME
	bld.new_task_gen(
		features = 'subst',
		source = 'main.py.in',
		target = 'main.py',
		install_path = '${DATAROOTDIR}/sushi/nigiri',
		chmod = 0755,
		dict = {'SUSHI_VERSION': bld.env.VERSION}
	)

	for man in ('nigiri.1',):
		# FIXME gzip
		bld.new_task_gen(
			features = 'subst',
			source = '%s.in' % (man),
			target = man,
			install_path = '${MANDIR}/man1',
			dict = {'SUSHI_VERSION': bld.env.VERSION}
		)
