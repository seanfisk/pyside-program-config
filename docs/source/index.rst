.. PySide Program Options documentation master file, created by
   sphinx-quickstart on Sun Jun 24 01:59:28 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PySide Program Options
======================

*Command-line argument parsing combined with the power of* :class:`QSettings`.

PySide Program Options leverages the excellent modules :mod:`argparse` and
:class:`QSettings` to become a full program configuration management tool. It
aims to be similar in purpose to Boost.Program_Options. The following features
are provided:

- required configuration items

  * fail when not provided
  * assume default value
  * call user-specified function
- optional configuration items

A User Guide will be coming soon. For the nitty-gritty details, see the API
documentation.

.. toctree::
   :maxdepth: 2

   api
   tests
   todo

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

