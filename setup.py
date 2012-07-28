#!/usr/bin/env python

# PySide Program Config setup script

import os
from pyside_program_config import metadata

# auto-install and download distribute
import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

install_requirements = []

test_requirements = [
    'pytest',
    'ludibrio'
]

# credit: <http://packages.python.org/an_example_pypi_project/setuptools.html>
# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# stolen from pytest's documentation
class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        # TODO: add in xdist, number of processors argument
        self.test_args = ['--verbose', 'tests']
        self.test_suite = True
    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        pytest.main(self.test_args)

# see here for more options:
# <http://packages.python.org/distribute/setuptools.html>
setup(name=metadata.title,
      version=metadata.version,
      author=metadata.authors[0],
      author_email=metadata.emails[0],
      maintainer=metadata.authors[0],
      maintainer_email=metadata.emails[0],
      url=metadata.url,
      description=metadata.description,
      long_description=read('README.rst'),
      download_url=metadata.url,
      # find a list of classifiers here:
      # <http://pypi.python.org/pypi?%3Aaction=list_classifiers>
      classifiers=[
          'Development Status :: 1 - Planning',
          'Environment :: MacOS X',
          'Environment :: Win32 (MS Windows)',
          'Environment :: X11 Applications :: Qt',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: ISC License (ISCL)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Application Frameworks',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      packages=find_packages(),
      install_requires=install_requirements,
      tests_require=test_requirements,
      cmdclass={'test': PyTest},
      zip_safe=False, # don't use eggs
      )
