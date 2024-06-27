.. raw:: html

    <h1 align="center">
    <img src="https://github.com/pyfar/gallery/raw/main/docs/resources/logos/pyfar_logos_fixed_size_sofar.png" width="300">
    </h1><br>

.. image:: https://badge.fury.io/py/sofar.svg
    :target: https://badge.fury.io/py/sofar
.. image:: https://readthedocs.org/projects/sofar/badge/?version=latest
    :target: https://sofar.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://circleci.com/gh/pyfar/sofar.svg?style=shield
    :target: https://circleci.com/gh/pyfar/sofar

Sofar is maybe the most complete Python package for the SOFA file format so
far. SOFA files store spatially distributed acoustic data such as impulse
responses or transfer functions. They are defined by the AES69-2022 standard
(see references). These are the key features of sofar

* Read, edit, and write SOFA files
* Add custom attributes to SOFA files
* Full Verification of the content of a SOFA files against AES69-2022
* Upgrade data that uses outdated SOFA conventions
* Open license allows unrestricted use
* sofar is tested using continuous integration on
* Uses a complete definition of the AES69-2022 standard (see references) maintained at `sofa_conventions`_

Getting Started
===============

The `sofa and SOFA notebook`_ gives an overview of the most important sofar
functionality and is a good starting point. For processing and visualizing data
inside SOFA files, we recommend the `pyfar package`_ that can read SOFA files
through `pyfar.io.read_sofa` and the in-depth examples contained in the
`pyfar example gallery`_. Check out `read the docs`_ for a complete
documentation of sofar. A more detailed introduction to the SOFA file format
is given by Majdak et. al. 2022 (see references below). All information is also
bundled at `pyfar.org`_.

Installation
============

Use pip to install sofar

.. code-block:: console

    $ pip install sofar

(Requires Python >= 3.8)

If the installation fails, please check out the `help section`_.

Contributing
============

Refer to the `contribution guidelines`_ for more information.

.. _sofa_conventions : https://github.com/pyfar/sofa_conventions
.. _sofa and SOFA notebook:  https://pyfar-gallery.readthedocs.io/en/latest/gallery/interactive/sofar_introduction.html
.. _pyfar package: https://pyfar.readthedocs.io
.. _pyfar example gallery: https://pyfar-gallery.readthedocs.io/en/latest/examples_gallery.html
.. _pyfar.org: https://pyfar.org
.. _read the docs: https://sofar.readthedocs.io
.. _help section: https://pyfar-gallery.readthedocs.io/en/latest/help
.. _contribution guidelines: https://sofar.readthedocs.io/en/stable/contributing.html

References
==========

AES69-2022: *AES standard for file exchange - Spatial acoustic data file
format*, Audio Engineering Society, Inc., New York, NY, USA.
(https://www.aes.org/publications/standards/search.cfm?docID=99)

P. Majdak, F. Zotter, F. Brinkmann, J. De Muynke, M. Mihocic, and M.
Noisternig, "Spatially Oriented Format for Acoustics 2.1: Introduction and
Recent Advances", *J. Audio Eng. Soc.*, vol. 70, no. 7/8, pp. 565-584,
Jul. 2022. DOI: https://doi.org/10.17743/jaes.2022.0026
