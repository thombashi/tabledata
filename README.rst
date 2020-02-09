.. contents:: **tabledata**
   :backlinks: top
   :depth: 2

Summary
---------
`tabledata <https://github.com/thombashi/tabledata>`__ is a Python library to represent tabular data. Used for pytablewriter/pytablereader/SimpleSQLite.

.. image:: https://badge.fury.io/py/tabledata.svg
    :target: https://badge.fury.io/py/tabledata
    :alt: PyPI package version

.. image:: https://img.shields.io/pypi/pyversions/tabledata.svg
    :target: https://pypi.org/project/tabledata
    :alt: Supported Python versions

.. image:: https://img.shields.io/travis/thombashi/tabledata/master.svg?label=Linux/macOS%20CI
    :target: https://travis-ci.org/thombashi/tabledata
    :alt: Linux/macOS CI status

.. image:: https://img.shields.io/appveyor/ci/thombashi/tabledata/master.svg?label=Windows%20CI
    :target: https://ci.appveyor.com/project/thombashi/tabledata/branch/master
    :alt: Windows CI status

.. image:: https://coveralls.io/repos/github/thombashi/tabledata/badge.svg?branch=master
    :target: https://coveralls.io/github/thombashi/tabledata?branch=master
    :alt: Test coverage

Installation
============

Install from PyPI
------------------------------
::

    pip install tabledata

Install from PPA (for Ubuntu)
------------------------------
::

    sudo add-apt-repository ppa:thombashi/ppa
    sudo apt update
    sudo apt install python3-tabledata


Dependencies
============
Python 2.7+ or 3.5+

Mandatory Python packages
----------------------------------
- `DataProperty <https://github.com/thombashi/DataProperty>`__ (Used to extract data types)
- `six <https://pypi.org/project/six/>`__
- `typepy <https://github.com/thombashi/typepy>`__

Optional Python packages
------------------------------------------------
- `loguru <https://github.com/Delgan/loguru>`__
    - Used for logging if the package installed
- `pandas <https://pandas.pydata.org/>`__
    - required to get table data as a pandas data frame

Test dependencies
-----------------
- `pytablewriter <https://github.com/thombashi/pytablewriter>`__
- `pytest <https://docs.pytest.org/en/latest/>`__
- `tox <https://testrun.org/tox/latest/>`__

Documentation
===============
https://tabledata.rtfd.io/

