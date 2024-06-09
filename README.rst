=====
sofar
=====

.. image:: https://badge.fury.io/py/sofar.svg
    :target: https://badge.fury.io/py/sofar
.. image:: https://readthedocs.org/projects/sofar/badge/?version=latest
    :target: https://sofar.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://circleci.com/gh/pyfar/sofar.svg?style=shield
    :target: https://circleci.com/gh/pyfar/sofar
.. image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/pyfar/gallery/main?labpath=docs/gallery/interactive/pyfar_introduction.ipynb


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

Getting Started
===============

The `pyfar workshop`_ gives an overview of the most important pyfar
functionality and is a good starting point. It is part of the
`pyfar example gallery`_ that also contains more specific and in-depth
examples that can be executed interactively without a local installation by
clicking the mybinder.org button on the respective example. The
`pyfar documentation`_ gives a detailed and complete overview of pyfar. All
these information are available from `pyfar.org`_.

Installation
============

Use pip to install sofar

.. code-block:: console

    $ pip install sofar

(Requires Python 3.8 or higher)

If the installation fails, please check out the `help section`_.

Contributing
============

Check out the `contributing guidelines`_ if you want to become part of pyfar.

.. _pyfar workshop: https://mybinder.org/v2/gh/pyfar/gallery/main?labpath=docs/gallery/interactive/pyfar_introduction.ipynb
.. _pyfar example gallery: https://pyfar-gallery.readthedocs.io/en/latest/examples_gallery.html
.. _pyfar documentation: https://pyfar.readthedocs.io
.. _pyfar.org: https://pyfar.org
.. _help section: https://pyfar-gallery.readthedocs.io/en/latest/help
.. _contributing guidelines: https://pyfar.readthedocs.io/en/stable/contributing.html
References
==========

AES69-2022: *AES standard for file exchange - Spatial acoustic data file
format*, Audio Engineering Society, Inc., New York, NY, USA.
(https://www.aes.org/publications/standards/search.cfm?docID=99)

P. Majdak, F. Zotter, F. Brinkmann, J. De Muynke, M. Mihocic, and M.
Noisternig, "Spatially Oriented Format for Acoustics 2.1: Introduction and
Recent Advances", *J. Audio Eng. Soc.*, vol. 70, no. 7/8, pp. 565-584,
Jul. 2022. DOI: https://doi.org/10.17743/jaes.2022.0026
