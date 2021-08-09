Examples
--------

If you are new to SOFA and/or sofar, this is a good place to start. SOFA is
short for Spatially Oriented Format for Acoustics and is an open file format
for saving acoustic data, as for example head-related impulse responses
(HRIRs). A good places to get more information about SOFA is
`sofaconventions.org`_.

To cover a variety of data, SOFA offers different `conventions`. A convention
defines, what data can be saved and how it is saved. You should always find the
most specific available convention for your data. This will help you to
identify relevant meta data that you should provide along the actual acoustic
data. Using sofar, a list of possible conventions can be obtained Using

.. code-block:: python

    import sofar as sf
    sf.list_conventions()

Let us assume, that you want to store head-related impulse responses (HRIRs).
In this case the most specific convention would be `SimpleFreeFieldHRIR`.
To create an empty SOFA object use

.. code-block:: python

    sofa = sf.create_sofa("SimpleFreeFieldHRIR")

The returned `sofa` object is a Python dictionary filled with the default
values of the `SimpleFreeFieldHRIR` convention. Note that ``sf.create_sofa()``
can return also return a sofa object that has only the mandatory entries.
However, it is recommended to start with all entries and discard empty optional
entries before saving the data.

To list all entries inside a sofa dictionary, try the following

.. code-block:: python

    sf.info(sofa, "all")

Note that this function can also be used to list only the mandatory or
optional fields.

Three different kinds of data can be stored in SOFA files

* **Attributes:**
    Attributes are meta data that is stored as strings. All entries that
    contain a colon (:) are attributes. There are two kinds of attributes.
    Global attributes give information about the entire data stored in a
    SOFA file. All entires starting with *GLOBAL:* are such attributes.
    Variable attribues hold meta data only for a specific variable. These
    attributes thus start with the name of the variable, e.g.,
    *ListenerPosition:Units*
* **Double Variables:**
    Variables of type *double* store numeric data and can be entered as
    numbers, lists, or numpy arrays.
* **String Variables:**
    Variables of type *string* store strings and can be entered as strings,
    lists of string, or numpy string arrays.

Lets take a look at an example

.. code-block:: python

    sf.info(sofa, "Data.IR")
    >>> SimpleFreeFieldHRIR 1.0 (SOFA version 2.0)
    >>> ------------------------------------------
    >>> type : double
    >>> mandatory : True
    >>> read only : False
    >>> default : [0, 0]
    >>> shape : mRn
    >>> comment :

`Data.IR` is a mandatory double variable of shape `mRn` in which the actual
HRIRs are stored. The letters M, R, and N are the `dimensions` of the SOFA
dictionary. They can be seen via

.. code-block:: python

    sf.info(sofa, "dimensions")
    >>> SimpleFreeFieldHRIR 1.0 (SOFA version 2.0)
    >>> ------------------------------------------
    >>> Dimensions
    >>>     M = 1 (measurements)
    >>>     N = 1 (samples/frequencies/SOS coefficients/SH coefficients)
    >>>     R = 2 (receiver)
    >>>     E = 1 (emitter)
    >>>     S = 0 (maximum string length)
    >>>     C = 3 (coordinate dimension, fixed)
    >>>     I = 1 (single dimension, fixed)

For the `SimpleFreeFieldHRIR` convention, `M` denotes the number of source
positions for which HRIRs are available, `R` is the number of ears - which is
two, and `N` gives the lengths of the HRIRs in samples. `S` is zero, because
the convention does not have any string variables. `C` is always three, because
coordinates are either given by x, y, and z values or by their azimuth,
elevation and radius in degree.

To enter data you should use the following

.. code-block:: python

    sf.set_value(sofa, "Data.IR", [1, 1])
    sf.set_value(sofa, "SourcePosition", [0, 0, 1])

Now, the SOFA dictionary contains one HRIR - which is 1 for the left ear and
1 for the right ear - for a source at 0 degree azimuth and elevation with a
radius of 1 meter. Note that you just entered a list for `Data.IR` although
it has to be a three-dimensional double variable. Don't worry about this, sofar
will convert this for you in the next step. Also note, that `sf.set_value` does
not return anything. Because Python dictionaries are mutable, all changes made
inside the function can also be seen after the function finished.

You should now fill all mandatory entries of the SOFA dictionary if you were
for real. For this is example we'll cut it here for the sake of brevity.

To write your SOFA dictionary to disk type

.. code-block:: python

    sf.write_sofa("your/path/to/SingleHRIR.sofa", sofa)

Before writing the data to disk the function `sf.update_api` is called,
which checks if the data you entered is consistent. Update API would for
example tell you that you are in trouble if you entered only one HRIR but two
source positions. If the check passed the file will be written to disk. It is
good to know that SOFA files are essentially netCDF4 files which is based
on HDF5. The can thus be viewed with `HDF View`_.

To read your sofa file you can use

.. code-block:: python

    sofa_read = sf.read_sofa("your/path/to/SingleHRIR.sofa")

And to see that the written and read files contain the same data you can check

.. code-block:: python

    sf.compare(sofa, sofa_read)
    >>> True

This is it for the tour of SOFA and sofar. For the detailed documentation of
sofar refer to the next page.


.. _sofaconventions.org: https://sofaconventions.org
.. _HDF view: https://www.hdfgroup.org/downloads/hdfview/