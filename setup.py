#!/usr/bin/env python

from __future__ import absolute_import, print_function, unicode_literals

from setuptools import setup
from os import system
from os.path import join
from sys import argv, exit
import re

with open(join('performant_pagination', '__init__.py')) as fh:
    version = re.search(r"__version__ = '([^']+)'", fh.read()).group(1)

if argv[-1] == 'publish':
    system("python setup.py sdist upload")
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    exit()

setup(
    name='performant_pagination',
    version=version,
    url='https://github.com/ross/performant-pagination/',
    license='BSD',
    description='',
    author='Ross McFarland',
    author_email='rwmcfa1@neces.com',
    packages=('performant_pagination',),
    test_suite='performant_pagination.runtests.runtests.main',
    install_requires=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
