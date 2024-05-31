from netCDF4 import Dataset
import numpy as np


class SofaStream():
    """
    Get data from SOFA-file without reading entire file into memory.

    :class:`SofaStream` opens a SOFA-file and retrieves only the requested
    data. See the examples below on how to use :class:`SofaStream`.

    If you want to use all the data from a SOFA-file use :class:`Sofa`
    class and :func:`read_sofa` function instead.

    Parameters
    ----------
    filename : str
        Full path to a SOFA-file

    Returns
    --------
    sofa_stream : SofaStream

    Examples
    --------
    Get an attribute from a SOFA-file:

        >>> import sofar as sf
        >>> filename = "path/to/file.sofa"
        >>> with sf.SofaStream(filename) as file:
        >>>     data = file.GLOBAL_RoomType
        >>>     print(data)
        free field

    Get a variable from a SOFA-file:

        >>> with SofaStream(filename) as file:
        >>>     data = file.Data_IR
        >>>     print(data)
        <class 'netCDF4._netCDF4.Variable'>
        float64 Data.IR(M, R, N)
        unlimited dimensions:
        current shape = (11950, 2, 256)
        filling on, default _FillValue of 9.969209968386869e+36 used

    What is returned is a `netCDF-variable`. To access the values (in this
    example the IRs) the variable needs to be sliced:

        >>> with SofaStream(filename) as file:
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
        # get netCDF4-attributes and -variable-keys from SOFA-file
        dset_variables = np.array([key for key in self._file.variables.keys()])
        dset_attributes = np.asarray(self._file.ncattrs())

        # remove delimiter from passed sofar-attribute
        name_netcdf = name.replace(
            'GLOBAL_', '').replace('Data_', 'Data.')

        # Handle variable-attributes (e.g. '_Units' and '_Type')
        var_attr = None
        if "_" in name_netcdf:
            name_netcdf, var_attr = name_netcdf.split('_')

        # get value if passed attribute points to a netCDF4-variable
        if name_netcdf in dset_variables:
            # get variable from SOFA-file
            self._data = self._file.variables[name_netcdf]
            if var_attr is not None:
                self._data = getattr(self._data, var_attr)

        # get value if passed attribute points to a netCDF4-attribute
        elif name_netcdf in dset_attributes:
            # get attribute value from SOFA-file
            self._data = self._file.getncattr(name_netcdf)

        else:
            raise AttributeError(f"{name} is not contained in SOFA-file")

        return self._data

    def inspect(self, file=None):
        """
        Get information about the data inside a SOFA-file

        Prints the values of all attributes and variables with six or less
        entries and the shapes and type of all numeric and string variables.
        When printing the values of arrays, single dimensions are discarded for
        easy of display, i.e., an array of shape (1, 3, 2) will be displayed as
        an array of shape (3, 2).

        Parameters
        ----------
        file : str
            Full path of a file under which the information is to be stored in
            plain text. The default ``None`` only print the information to the
            console.
        """

        # Header of inspect-print
        info_str = (
            f"{self._file.getncattr('SOFAConventions')} "
            f"{self._file.getncattr('SOFAConventionsVersion')} "
            f"(SOFA version {self._file.getncattr('Version')})\n")
        info_str += "-" * len(info_str) + "\n"

        # information for attributes
        for attr in self._file.ncattrs():

            value = self._file.getncattr(attr)
            sofar_attr = f"GLOBAL_{attr}"
            info_str += sofar_attr + ' : ' + str(value) + '\n'

        # information for variables
        for key in self._file.variables.keys():
            # get values, shape and dimensions
            data = self._file[key]
            shape = data.shape
            dimensions = data.dimensions

            # add variable name to info-string
            info_str += key.replace('.', '_') + ' : '

            # pad shape if required (trailing single dimensions are
            # discarded following the numpy default)
            while len(shape) < len(dimensions):
                shape += (1, )

            # add value for scalars
            if data.size == 1:
                info_str += str(data[:][0]) + '\n'

            # Handle multidimensional data
            else:
                # make verbose shape, e.g., '(M=100, R=2, N=128, '
                shape_verbose = "("
                for s, d in zip(shape, dimensions):
                    shape_verbose += f"{d}={s}, "

                # add shape information
                info_str += shape_verbose[:-2] + ")\n"
                # add value information if not too much
                if data.size < 7:
                    info_str += "  " + \
                        str(np.squeeze(data[:])).replace("\n", "\n  ") + "\n"

            # Add variable-attributes to info string (e.g. 'Type' or 'Units)
            for att_ in [a for a in self._file[key].ncattrs()]:
                info_str += (key.replace('.', '_') + f'_{att_} : '
                             + getattr(data, att_) + '\n')

        # write to text file
        if file is not None:
            with open(file, 'w') as f_id:
                f_id.write(info_str + "\n")

        # print to console
        print(info_str)
