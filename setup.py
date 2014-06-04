#!/bin/env python
# coding: utf-8
# vim:et:sta:sw=2:sts=2:ts=2:tw=0:

import os
import codecs
import re
from setuptools import setup, find_packages


def read(*paths):
  """Build a file path from *paths* and return the contents."""
  with codecs.EncodedFile(open(os.path.join(*paths), 'rb'), 'utf-8') as f:
    return f.read()


def find_version(*file_paths):
  version_file = read(*file_paths)
  version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
  if version_match:
    return version_match.group(1)
  raise RuntimeError("Unable to find version string.")

config = {
  'name': 'urwidm',
  'description': 'More widgets for Urwid',
  'long_description': read('README.rst'),
  'license': 'LGPL',
  'author': 'Cyrille Pontvieux',
  'author_email': 'jrd@salixos.org',
  'version': find_version('urwidm', '__init__.py'),
  'url': 'https://github.com/jrd/urwidmore/',
  'download_url': 'https://github.com/jrd/urwidmore/archive/master.zip',
  'packages': find_packages(exclude=['tests']),
  'include_package_data': True,
  'test_suite': 'tests',
  'classifiers': [  # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Environment :: Console :: Curses',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    'Operating System :: POSIX',
    'Operating System :: Unix',
    'Operating System :: MacOS :: MacOS X',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development :: Widget Sets',
  ],
}
setup(**config)
