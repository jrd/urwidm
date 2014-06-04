#!/usr/bin/env python
# coding: utf8
# vim:et:sta:st=2:ts=2:tw=0:
from __future__ import division, unicode_literals, print_function, absolute_import
import sys
import os
import shutil
from glob import glob
import pip
from pip.util import get_installed_distributions as pip_get_installed


MODULE_NAME = 'urwidm'
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))


def usage():
  print("""\
Usage: make ACTION
ACTION:
  clean: clean the mess
  build: create a .whl (python wheel) file
  install [global]: install the wheel file, eventually globaly
  info: information about pylibsalt, if installed
""")


def clean():
  shutil.rmtree('wheelhouse', True)


def pip_run(*args):
  pip.main(list(args))
  pip.logger.consumers = []


def build():
  clean()
  pip_run('wheel', '.')


def install(local=True):
  build()
  wheel_file = glob('wheelhouse/*.whl')[0]
  if local:
    pip_run('install', '--user', wheel_file)
  else:
    pip_run('install', wheel_file)


def info():
  if [d.key for d in pip_get_installed() if d.key == MODULE_NAME]:
    pip_run('show', MODULE_NAME)
  else:
    print("pylibsalt not installed, try ./make install or ./make install local", file=sys.stderr)
    sys.exit(1)

args = sys.argv[1:]
if not args:
  args = ['build']
while args:
  arg = args[0]
  args = args[1:]
  if arg == 'help' or arg == '--help':
    usage
    sys.exit(0)
  elif arg == 'clean':
    clean()
  elif arg == 'build':
    build()
  elif arg == 'install':
    if args and args[0] == 'global':
      args = args[1:]
      install(False)
    else:
      install()
  elif arg == 'info':
    info()
  else:
    usage()
    sys.exit(1)
