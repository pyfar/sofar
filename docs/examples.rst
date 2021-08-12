Examples
--------

If you are new to SOFA and/or sofar, this is a good place to start. SOFA is
short for Spatially Oriented Format for Acoustics and is an open file format
for saving acoustic data, as for example head-related impulse responses
(HRIRs). A good places to get more information about SOFA is
`sofaconventions.org`_.

To cover a variety of data, SOFA offers different `conventions`. A convention
defines, what data can be saved and how it is saved. You should always find the
most specific convention for your data. This will help you to identify relevant
data and meta data that you should provide along the actual acoustic data.
Using sofar, a list of possible conventions can be obtained Using

.. code-block:: python

    import sofar as sf
    sf.list_conventions()

Let us assume, that you want to store head-related impulse responses (HRIRs).
In this case the most specific convention is `SimpleFreeFieldHRIR`. To create
an empty SOFA object use

.. code-block:: python

    sofa = sf.Sofa("SimpleFreeFieldHRIR")

The return value `sofa` is a sofar.Sofa object filled with the default values
of the `SimpleFreeFieldHRIR` convention. Note that ``sf.Sofa()`` can return
return a sofa object that has only the mandatory attributes. However, it is
recommended to start with all attributes and discard empty optional attributes
before saving the data.

To list all attributes inside a SOFA object, try the following

.. code-block:: python

    sofa.info("all")

Note that this function can also be used to list only the mandatory or
optional fields, and to list different kinds of information such as the
data types, default values, or shapes.

Three different kinds of data can be stored in SOFA files. Use
``sofa.info("type")`` to list them:

* **Attributes:**
    Attributes are meta data that is stored as strings. There are two kinds of
    attributes. Global attributes give information about the entire data stored
    in a SOFA file. All entires starting with *GLOBAL* are such attributes.
    Variable attributes hold meta data only for a specific variable. These
    attributes thus start with the name of the variable, e.g.,
    *ListenerPosition_Units*
* **Double Variables:**
    Variables of type *double* store numeric data and can be entered as
    numbers, lists, or numpy arrays.
* **String Variables:**
    Variables of type *string* store strings and can be entered as strings,
    lists of string, or numpy string arrays.

Lets take a look and list all informations for only one attribute of the SOFA
object (note that all data in Python classes is called attribute - regardless
of the data type explaned above):

.. code-block:: python

    sofa.info("Data_IR")
    >>> SimpleFreeFieldHRIR 1.0 (SOFA version 2.0)
    >>> ------------------------------------------
    >>> type : double
    >>> mandatory : True
    >>> read only : False
    >>> default : [0, 0]
    >>> shape : MRN
    >>> comment :

`Data_IR` is a mandatory double variable of shape `MRN` in which the actual
HRIRs are stored. The letters M, R, and N are the `dimensions` of the SOFA
dictionary. They can be seen via

.. code-block:: python

    sofa.info("dimensions")
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

Data can simply be obtained and entered

.. code-block:: python

    sofa.Data_IR  # prints [0, 0]
    sofa.Data_IR = [1, 1]
    sofa.SourcePosition = [90, 0, 1.5]

Now, the SOFA dictionary contains one HRIR - which is ``1`` for the left ear
and ``1`` for the right ear - for a source at ``0`` degree azimuth, ``90``
degree elevation and a radius of ``1.5`` meter. Note that you just entered a
list for `Data_IR` although it has to be a three-dimensional double variable.
Don't worry about this, sofar will convert this for you in the next step.

You should now fill all mandatory entries of the SOFA dictionary if you were
for real. For this is example we'll cut it here for the sake of brevity.

To write your SOFA dictionary to disk type

.. code-block:: python

    sf.write_sofa("your/path/to/SingleHRIR.sofa", sofa)

Before writing the data to disk the function `Sofa.verify` is called,
which checks if the data you entered is consistent and updates the SOFA object.
This would for example tell you that you are in trouble if you entered only one
HRIR but two source positions. If the check passed the file will be written to
disk. It is good to know that SOFA files are essentially netCDF4 files which is
based on HDF5. The can thus be viewed with `HDF View`_.

To read your sofa file you can use

.. code-block:: python

    sofa_read = sf.read_sofa("your/path/to/SingleHRIR.sofa")

And to see that the written and read files contain the same data you can check

.. code-block:: python

    sf.compare_sofa(sofa, sofa_read)
    >>> True

This is it for the tour of SOFA and sofar. For the detailed documentation of
sofar refer to the next page.


.. _sofaconventions.org: https://sofaconventions.org
.. _HDF view: https://www.hdfgroup.org/downloads/hdfview/