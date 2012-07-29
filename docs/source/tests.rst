=======
 Tests
=======

Tests are written and run using :mod:`pytest`. To run all the tests, run the
following in the project root directory::

   python setup.py test

This will run all the tests in verbose mode using all the machine's available
CPUs.

For more fine-grained control, the ``py.test`` runner may be used. Here is an
example using two CPUs and verbose mode, much the same configuration as is run
with the above command::

   py.test --verbose -n 2 tests
