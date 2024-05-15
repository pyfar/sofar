from netCDF4 import Dataset
import numpy as np

class Sofastream():
    """
    Get specific data from sofa-file without reading entire file into memory.

    :class:`Sofastream` opens a sofa-file and retreives only the requested
    data. To access certain data just append its name to your
    :class:`Sofastream`-instance, e.g. ``'.GLOBAL_RoomType'``.
    :class:`Sofastream` uses the namespace of sofar – for more information on
    available data and its associated names refer to the :ref:`conventions
    section <conventions_introduction>`. Also make sure to check the examples
    below on how to use :class:`Sofastream`.

    Parameters
    ----------
    filename : str
        Full path to a sofa-file

    Returns
    --------
    sofastream : Sofastream

    Notes
    -----
    Accessing data:

    Sofastream is supposed to be used within a with-statement. To acces data
    append the corresponding name to your instance of :class:`Sofastream`.

    Depending on the type of the requested data you either get the values
    directly or need to slice the returned variable:

    - If an attribute is called, its value is returned directly.
    - If a variable is called, a netCDF4-variable is returned. To get the
      values it needs to be sliced (see examples).

    Examples
    --------
    Get an attribute from a sofa-file:

        >>> from sofar import Sofastream
        >>> filename = "path/to/file.sofa"
        >>> with Sofastream(filename) as file:
        >>>     data = file.GLOBAL_RoomType
        >>>     print(data)
        free field

    Get a variable from a sofa-file:

        >>> with Sofastream(filename) as file:
        >>>     data = file.Data_IR
        >>>     print(data)
        <class 'netCDF4._netCDF4.Variable'>
        float64 Data.IR(M, R, N)
        unlimited dimensions:
        current shape = (11950, 2, 256)
        filling on, default _FillValue of 9.969209968386869e+36 used

    What is returned is a `netCDF-variable`. To access the values (in this
    example the IRs) the variable needs to be sliced:

        >>> with Sofastream(filename) as file:
        >>>     data = file.Data_IR
        >>>     # get all values
        >>>     all_irs = data[:]
        >>>     print(all_irs.shape)
        (11950, 2, 256)
        >>>     # get data from first channel
        >>>     specific_irs = data[:,0,:]
        >>>     print(specific_irs.shape)
        (11950, 256)
    """

    def __init__(self, filename):
        self._filename = filename

    def __enter__(self):
        self._file = Dataset(self._filename, mode="r")
        return self

    def __exit__(self, *args):
        self._file.close()

    def __getattr__(self, name):
        # get netCDF4-attributes and -variable-keys from sofa-file
        dset_variables = np.array([key for key in self._file.variables.keys()])
        dset_attributes = np. asarray(self._file.ncattrs())

        # remove delimiter from passed sofar-attribute
        name = name.replace('_', '')
        name = name.replace('GLOBAL', '')

        # remove delimiter from netCDF4-attributes and -variables
        variables_to_search = np.char.replace(dset_variables, '.', '')
        attributes_to_search = np.char.replace(dset_attributes, ':', '')

        # get value if passed attribute points to a netCDF4-variable
        if name in variables_to_search:
            # get variable name in netCDF-namespace
            idx = np.where(name == variables_to_search)
            key = dset_variables[idx][0]
            # get variable from sofa-file
            self._data = self._file.variables[key]

        # get value if passed attribute points to a netCDF4-attribute
        elif name in attributes_to_search:
            # get attribute name in netCDF-namespace
            idx = np.where(name == attributes_to_search)
            key = dset_attributes[idx][0]
            # get attribute value from sofa-file
            self._data = self._file.getncattr(key)

        else:
            raise ValueError("attribute is not in dataset")

        return self._data
