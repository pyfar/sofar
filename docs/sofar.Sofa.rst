.. _sofar_SOFA:

SOFA objects
============

Sofar offers two classes to handle data from SOFA files:
The :py:class:`~sofar.Sofa` class is used to read and write entire SOFA files.
To open a SOFA file without reading the entire file into memory,
:py:class:`~sofar.SofaStream` enables partial reading of data.

This section documents sofar SOFA objects and SofaStream. Functions that work
on SOFA objects are described in the :ref:`sofar_functions` guide. For examples
on how to use sofar refer to the
:ref:`sofa and SOFA <gallery:/gallery/interactive/sofar_introduction.ipynb>`
examples.

.. autoclass:: sofar.Sofa
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members:

.. autoclass:: sofar.SofaStream
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members:
