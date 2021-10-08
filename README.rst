======
Readme
======

Sofar is maybe the most complete Python package for the SOFA file format so
far. SOFA files store spatially distributed acoustic data such as impulse
responses or transfer functions. These are the sofar key features

* Based on the official SOFA conventions from the `Matlab/Octave API`_
* Read and write support for SOFA files
* Add custom attributes to SOFA files
* Verify content of a SOFA file with respect to the data type and shape
* Open license allows unrestricted use
* sofar is tested using continuous integration on Travis CI

Installation
============

Use pip to install sofar

.. code-block:: console

    $ pip install sofar

(Requires Python >= 3.7)

Getting Started
===============

Check out `read the docs`_ for example use cases and the complete
documentation. Packages related to sofar are listed at `pyfar.org`_. For more
information on the SOFA file format visit `sofaconventions.org`_.

Contributing
============

Refer to the `contribution guidelines`_ for more information.

.. _Matlab/Octave API : https://github.com/sofacoustics/API_MO
.. _contribution guidelines: https://github.com/pyfar/sofar/blob/develop/CONTRIBUTING.rst
.. _pyfar.org: https://pyfar.org
.. _read the docs: https://sofar.readthedocs.io/en/latest
.. _sofaconventions.org: https://sofaconventions.org
