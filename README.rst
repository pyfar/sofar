======
Readme
======

Sofar is maybe the most complete Python package for the SOFA file format so
far. SOFA files store spatially distributed acoustic data such as impulse
responses or transfer functions. They are defined by the AES69-2022 standard
(see references). These are the key features of sofar

* Uses a complete definition of the AES69-2022 standard (see references) maintained at `sofa_conventions`_
* Read, edit, and write SOFA files
* Add custom attributes to SOFA files
* Full Verification of the content of a SOFA files against AES69-2022
* Upgrade data that uses outdated SOFA conventions
* Open license allows unrestricted use
* sofar is tested using continuous integration on

Installation
============

Use pip to install sofar

.. code-block:: console

    $ pip install sofar

(Requires Python >= 3.8)

Getting Started
===============

Check out `read the docs`_ for example use cases a quick introduction to SOFA
and sofar, and the complete documentation. A more detailed introduction to SOFA
is given by Majdak et. al. 2022 (see references below) Packages related to
sofar are listed at `pyfar.org`_. For more information on the SOFA file format
visit `sofaconventions.org`_.

Contributing
============

Refer to the `contribution guidelines`_ for more information.

.. _sofa_conventions : https://github.com/pyfar/sofa_conventions
.. _contribution guidelines: https://github.com/pyfar/sofar/blob/develop/CONTRIBUTING.rst
.. _pyfar.org: https://pyfar.org
.. _read the docs: https://sofar.readthedocs.io/en/stable
.. _sofaconventions.org: https://sofaconventions.org

References
==========

AES69-2022: *AES standard for file exchange - Spatial acoustic data file
format*, Audio Engineering Society, Inc., New York, NY, USA.
(https://www.aes.org/publications/standards/search.cfm?docID=99)

P. Majdak, F. Zotter, F. Brinkmann, J. De Muynke, M. Mihocic, and M.
Noisternig, "Spatially Oriented Format for Acoustics 2.1: Introduction and
Recent Advances", *J. Audio Eng. Soc.*, vol. 70, no. 7/8, pp. 565-584,
Jul. 2022. DOI: https://doi.org/10.17743/jaes.2022.0026
