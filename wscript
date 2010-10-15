#!/usr/bin/env python

import Utils

APPNAME = 'nigiri'
VERSION = '1.4.0'

srcdir = '.'
blddir = 'build'

def configure (conf):
	conf.check_tool('gnu_dirs')
	conf.check_tool('misc')

	conf.find_program('gzip', var = 'GZIP')

	conf.env.VERSION = VERSION

	conf.sub_config('po')

def build (bld):
	bld.add_subdirs('po')

	bld.install_files('${DATAROOTDIR}/sushi/nigiri', bld.glob('*.py'))
	bld.install_files('${DATAROOTDIR}/sushi/nigiri/extends', bld.glob('extends/*.py'))
	bld.install_files('${DATAROOTDIR}/sushi/nigiri/helper', bld.glob('helper/*.py'))
	bld.install_files('${DATAROOTDIR}/sushi/nigiri/plugins', bld.glob('plugins/*.py'))

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
		bld.new_task_gen(
			features = 'subst',
			source = '%s.in' % (man),
			target = man,
			install_path = None,
			dict = {'SUSHI_VERSION': bld.env.VERSION}
		)

	bld.add_group()

	for man in ('nigiri.1',):
		bld.new_task_gen(
			source = man,
			target = '%s.gz' % (man),
			rule = '${GZIP} -c ${SRC} > ${TGT}',
			install_path = '${MANDIR}/man1'
		)
