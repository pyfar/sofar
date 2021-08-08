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

    sofa = sf.info(sofa, "all")

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

    sofa = sf.info(sofa, "Data.IR")
    >>> SimpleFreeFieldHRIR 1.0 (SOFA version 2.0)
    >>> ------------------------------------------
    >>> type : double
    >>> mandatory : True
    >>> read only : False
    >>> default : [0, 0]
    >>> dimensions : mRn
    >>> comment :

`Data.IR` is a mandatory double variable in which the actual HRIRs are stored.

TODO:
* What are dimensions
* What dimensions are there
* Example for entering data
* Example for writing sofa file
* Example for reading sofa file
* Mention other functions briefly


.. _sofaconventions.org: https://sofaconventions.org