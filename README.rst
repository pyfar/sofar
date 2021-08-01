========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/sofar/badge/?style=flat
    :target: https://readthedocs.org/projects/sofar
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/f-brinkmann/sofar.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/f-brinkmann/sofar

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/f-brinkmann/sofar?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/f-brinkmann/sofar

.. |requires| image:: https://requires.io/github/f-brinkmann/sofar/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/f-brinkmann/sofar/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/f-brinkmann/sofar/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/f-brinkmann/sofar

.. |version| image:: https://img.shields.io/pypi/v/sofar.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/sofar

.. |commits-since| image:: https://img.shields.io/github/commits-since/f-brinkmann/sofar/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/f-brinkmann/sofar/compare/v0.1.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/sofar.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/sofar

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/sofar.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/sofar

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/sofar.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/sofar


.. end-badges

maybe the most intuitive python package for SOFA files so far

* Free software: BSD 3-Clause License

Installation
============

::

    pip install sofar

Documentation
=============

https://sofar.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
