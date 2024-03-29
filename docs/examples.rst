.. _quick_tour:

Quick tour of SOFA and sofar
----------------------------

If you are new to SOFA and/or sofar, this is a good place to start. SOFA is
short for *Spatially Oriented Format for Acoustics* and is an open file format
for saving acoustic data, as for example head-related impulse responses
(HRIRs). A good places to get more information about SOFA are

* :ref:`Documentation of the SOFA conventions <conventions_introduction>`
* The `SOFA paper <https://doi.org/10.17743/jaes.2022.0026>`_
* `sofaconventions.org`_.
* The SOFA standard `AES69-2022 <https://www.aes.org/publications/standards/search.cfm?docID=99>`_

Creating SOFA objects
=====================

To cover a variety of data, SOFA offers different `conventions`. A convention
defines, what data can be saved and how it is saved. You should always find the
most specific convention for your data. This will help you to identify relevant
data and meta data that you should provide along the actual acoustic data.
Using sofar, a list of possible conventions can be obtained with

.. code-block:: python

    import sofar as sf
    sf.list_conventions()

Let us assume, that you want to store head-related impulse responses (HRIRs).
In this case the most specific convention is `SimpleFreeFieldHRIR`. To create
a SOFA object use

.. code-block:: python

    sofa = sf.Sofa("SimpleFreeFieldHRIR")

The return value `sofa` is a :code:`sofar.Sofa` object filled with the default
values of the `SimpleFreeFieldHRIR` convention. Note that ``sf.Sofa()`` can
also return a sofa object that has only the mandatory attributes. However, it
is recommended to start with all attributes and discard empty optional
attributes before saving the data.

.. _getting_information_about_SOFA_objects:

Getting information about SOFA objects
======================================

To get an overview of the convention, go to the
:ref:`documentation of the SOFA conventions <conventions_introduction>`.

You might have noted from the documentation that three different kinds of
data types can be stored in SOFA files:

* **Attributes:**
    Attributes are meta data stored as strings. There are two kinds of
    attributes. Global attributes give information about the entire data stored
    in a SOFA file. All entires starting with *GLOBAL* are such attributes.
    Specific attributes hold meta data for a certain variable. These attributes
    thus start with the name of the variable followed by an underscore, e.g.,
    *ListenerPosition_Units*. An exception to this rule are the data variables,
    e.g, *Data_IR* is not an attribute but a double variable.
* **Double Variables:**
    Variables of type *double* store numeric data and can be entered as
    numbers, lists, or numpy arrays.
* **String Variables:**
    Variables of type *string* store strings and can be entered as strings,
    lists of string, or numpy string arrays.

The data can be mandatory, optional, and read only and must have a shape
(dimension in SOFA language) according to the underlying convention. Read on
for more information.

To get a quick insight into SOFA objects use

* ``sofa.inspect`` prints the data stored in a SOFA object or at least gives
  the shape in case of large arrays that would clutter the output. This is
  helpful when reading data from an existing SOFA object.
* ``sofa.list_dimensions`` prints the dimensions of the data inside the SOFA
  object.
* ``sofa.get_dimension`` returns the size of a specific dimension.

For the *SimpleFreeFieldHRIR* SOFA object we have the following dimensions

.. code-block:: python

    sofa.list_dimensions
    >>> R = 2 receiver (set by ReceiverPosition of dimension RCI, RCM)
    >>> E = 1 emitter (set by EmitterPosition of dimension ECI, ECM)
    >>> M = 1 measurements (set by Data_IR of dimension MRN)
    >>> N = 1 samples (set by Data_IR of dimension MRN)
    >>> C = 3 coordinate dimensions, fixed
    >>> I = 1 single dimension, fixed
    >>> S = 0 maximum string length

In this case, `M` denotes the number of source
positions for which HRIRs are available, `R` is the number of ears - which is
two - and `N` gives the lengths of the HRIRs in samples. `S` is zero, because
the convention does not have any string variables. `C` is always three, because
coordinates are either given by x, y, and z values or by their azimuth,
elevation and radius in degree.

It is important to be aware of the dimensions and enter data as determined by
the convention. SOFA sets the `dimensions`
implicitly. This means the dimensions are derived from the data itself, as
indicated by the output of :code:`sofa.list_dimensions` above (*set by...*). In
some cases, variables can have different shapes. An example for this is the
`ReceiverPosition` which can be of shape RCI or RCM. To get a dimension as a
variable use

.. code-block:: python

    sofa.get_dimension("N)
    >>> N = 1

Let's assume you downloaded a SOFA file from the `FABIAN database <https://depositonce.tu-berlin.de/handle/11303/6153.5>`_
and want to quickly inspect it. You could use

.. code-block:: python

    sofa = sf.read_sofa("FABIAN_HRIR_measured_HATO_0.sofa")
    sofa.inspect()
    >>> GLOBAL_License : Creative Commons (CC-BY). Visit http://creativecommons.org/licenses/by/4.0/ for licence details.
    >>> GLOBAL_Organization : Audio Communication Group, TU Berlin, Germany (www.ak.tu-berlin.de)
    >>> ReceiverPosition : (R=2, C=3, I=1)
    >>>   [[ 0.      0.0662  0.    ]
    >>>    [ 0.     -0.0662  0.    ]]
    >>> Data_IR : (M=11950, R=2, N=256)
    >>> Data_SamplingRate : 44100.0
    >>> Data_SamplingRate_Units : hertz

Note that the above does not show the entire information for the sake of
brevity. This will most likely give you a better idea of the data then
looking at the definition of the convention or calling ``sofa.list_dimensions``.

Adding data to SOFA objects
===========================

Data can simply be obtained and entered

.. code-block:: python

    sofa.Data_IR  # prints [0, 0]
    sofa.Data_IR = [1, 1]
    sofa.SourcePosition = [90, 0, 1.5]

Now, the SOFA object contains a single HRIR - which is ``1`` for the left
ear and ``1`` for the right ear - for a source at ``0`` degree azimuth, ``90``
degree elevation and a radius of ``1.5`` meter. Note that you just entered a
list for `Data_IR` although it has to be a three-dimensional double variable.
Sofar handles this in two steps.

1. When entering data as lists it is converted to a numpy array with at least two dimensions.
2. Missing dimensions are appended when writing the SOFA object to disk.

You should now fill all mandatory entries of the SOFA object if you were
for real. For this example we'll cut it here for the sake of brevity. Let
us, however, delete an optional entry that we do not need at this point

.. code-block:: python

    sofa.delete("SourceUp")

In some cases you might want to add custom data - although third party
applications most likely won't make use of non-standardized data. Try this
to add a temperature value and unit

.. code-block:: python

    sofa.add_variable("Temperature", 25.1, "double", "MI")
    sofa.add_attribute("Temperature_Units", "degree Celsius")


After entering the data, the SOFA object should be verified to make sure that
your data can (most likely) be read by other applications.

.. code-block:: python

    sofa.verify()

This will check the following

- Are all mandatory data contained?
- Are the names of variables and attributes in accordance with the SOFA
  standard?
- Are the data types in accordance with the SOFA standard?
- Are the dimensions of the variables consistent and in accordance
  to the SOFA standard?
- Are the values of attributes consistent and in accordance to the
  SOFA standard?

If any violations are detected, an error is raised.

Reading and writing SOFA objects
================================

Note that you usually do not need to call ``sofa.verify()`` separately  because
it is by default called if you create write or read a SOFA object. To write
your SOFA object to disk type

.. code-block:: python

    sf.write_sofa("your/path/to/SingleHRIR.sofa", sofa)

It is good to know that SOFA files are essentially netCDF4 files which is
based on HDF5. They can thus be viewed with `HDF View`_.

To read your sofa file you can use

.. code-block:: python

    sofa_read = sf.read_sofa("your/path/to/SingleHRIR.sofa")

And to see that the written and read files contain the same data you can check

.. code-block:: python

    sf.equals(sofa, sofa_read)
    >>> True

Upgrading SOFA files
====================

SOFA conventions might get updates to fix bugs in the conventions, in case
new conventions are introduced, or in case conventions get deprecated. To find
out if SOFA data from a file is up to data load it and call

.. code-block:: python

    sofa.upgrade_convention()

which will list upgrade choices or let you know that the convention is already up
to date.

Next steps
==========

For detailed information about sofar refer to the :ref:`sofar_SOFA` and :ref:`sofar_functions` documentation.
For examples on how to work with the data inside SOFA files refer to :ref:`working_with_sofa`.


.. _sofaconventions.org: https://sofaconventions.org
.. _HDF view: https://www.hdfgroup.org/downloads/hdfview/