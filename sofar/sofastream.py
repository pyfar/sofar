"""
Read desired data from SOFA-file directly from disk without loading entire
file into memory.
"""
from netCDF4 import Dataset
import numpy as np

import sofar as sf

from .io import _format_value_from_netcdf


class _LazyArray(np.ndarray):
    """Represent a NetCDF numeric variable without reading its data."""

    def __new__(cls, shape, dtype):
        data = np.array(0, dtype=dtype)
        strides = (0, ) * len(shape)
        return np.lib.stride_tricks.as_strided(
            data, shape=shape, strides=strides).view(cls)

    def copy(self, order='C'):
        """Return a view instead of materializing the full array."""
        _ = order
        return self


class SofaStream():
    """
    Read desired data from SOFA-file directly from disk without loading entire
    file into memory.

    :class:`SofaStream` opens a SOFA-file and retrieves only the requested
    data. It can also verify the file against the SOFA convention using the
    same checks as :py:func:`~sofar.Sofa.verify`.

    If you want to use all the data from a SOFA-file use :class:`Sofa`
    class and :func:`read_sofa` function instead.

    Parameters
    ----------
    filename : str
        Full path to a SOFA-file

    Returns
    -------
    sofa_stream : SofaStream
        A SofaStream object which reads directly from the file.

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
        """Initialize a new SofaStream object (see documentation above)."""
        self._filename = filename

    def __enter__(self):
        """
        Executed when entering a ``with`` statement
        (see documentation above).
        """
        self._file = Dataset(self._filename, mode="r")
        return self

    def __exit__(self, *args):
        """
        Executed when exiting a ``with`` statement
        (see documentation above).
        """
        self._file.close()

    def verify(self, issue_handling="raise", mode="write"):
        """
        Verify a SOFA file against the SOFA standard.

        See :py:func:`~sofar.Sofa.verify` for details.

        This method checks whether mandatory data are present, names, data
        types, and dimensions follow the SOFA standard, and attribute values
        are consistent with the SOFA standard. Missing mandatory data raise an
        error when ``issue_handling='raise'``; otherwise, they are added with
        their default value and a warning is given.

        Numeric variables are represented by lazy placeholders, so only their
        type and dimensions are checked without loading their contents into
        memory. String variables are loaded because their values and lengths
        can be relevant for convention verification.

        A detailed set of validation rules can be found at
        https://github.com/pyfar/sofar/tree/main/sofar/verification_rules

        Parameters
        ----------
        issue_handling : str, optional
            Defines how detected issues are handled.

            ``'raise'``
                Warnings and errors are raised if issues are detected.
            ``'print'``
                Issues are printed without raising warnings and errors.
            ``'return'``
                Issues are returned as a string but neither raised nor printed.

            The default is ``'raise'``.
        mode : str, optional
            The SOFA standard is more strict for writing data than for reading
            data.

            ``'write'``
                All units (e.g., ``'meter'``) must be lower case.
            ``'read'``
                Units can contain upper case letters (e.g., ``'Meter'``).

            The default is ``'write'``.

        Returns
        -------
        issues : str, None
            Detected issues as a string. None if no issues were detected. Note
            that this is only returned if ``issue_handling='return'``.
            Examples
            ----------

            >>> import sofar
            >>>
            >>> with sofar.SofaStream("path/to/your.sofa") as file:
            >>>     file.verify()
        """
        return self._verify_open_file(issue_handling, mode)

    def _verify_open_file(self, issue_handling, mode):
        """Verify the currently opened NetCDF file."""
        return self._read_open_file_for_verification().verify(
            issue_handling=issue_handling, mode=mode)

    def _read_open_file_for_verification(self):
        """Read the currently opened file using lazy numeric variables."""
        # get SOFA object with default values and convention metadata
        sofa = sf.Sofa(
            self._file.SOFAConventions,
            version=self._file.SOFAConventionsVersion,
            verify=False)
        sofa.protected = False

        # NetCDF attribute _Encoding is skipped when reading SOFA files
        skip = ["_Encoding"]
        all_attr = []

        # load global attributes
        for attr in self._file.ncattrs():
            value = getattr(self._file, attr)
            key = f"GLOBAL_{attr}"
            all_attr.append(key)

            if not hasattr(sofa, key):
                sofa._add_custom_api_entry(key, value, None, None, "attribute")
                sofa.protected = False
            else:
                setattr(sofa, key, value)

        # load variable metadata and string values
        for var in self._file.variables.keys():
            netcdf_variable = self._file[var]
            key = var.replace(".", "_")
            all_attr.append(key)

            if netcdf_variable.datatype == "S1":
                value = _format_value_from_netcdf(netcdf_variable[:], var)
                dtype = "string"
            else:
                value = _LazyArray(
                    netcdf_variable.shape, netcdf_variable.dtype)
                dtype = "double"

            if hasattr(sofa, key):
                setattr(sofa, key, value)
            else:
                dimensions = "".join(list(netcdf_variable.dimensions))
                sofa._add_custom_api_entry(
                    key, value, None, dimensions, dtype)
                sofa.protected = False

            # load variable attributes
            for attr in [a for a in netcdf_variable.ncattrs()
                         if a not in skip]:
                value = getattr(netcdf_variable, attr)
                attr_key = key + "_" + attr
                all_attr.append(attr_key)

                if not hasattr(sofa, attr_key):
                    sofa._add_custom_api_entry(
                        attr_key, value, None, None, "attribute")
                    sofa.protected = False
                else:
                    setattr(sofa, attr_key, value)

        # remove default entries that were not contained in the file
        attrs = [attr for attr in sofa.__dict__.keys()
                 if not attr.startswith("_")]
        for attr in attrs:
            if attr not in all_attr:
                delattr(sofa, attr)

        sofa.protected = True
        return sofa

    def __getattr__(self, name):
        """
        Executed when accessing data within a with statement
        (see documentation above).
        """
        # get netCDF4-attributes and -variable-keys from SOFA-file
        dset_variables = np.array(list(self._file.variables.keys()))
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

    @property
    def list_dimensions(self):
        """
        Print the dimensions of the SOFA-file.

        See :py:func:`~SofaStream.inspect` to see the shapes of the data inside
        the SOFA-file and :py:func:`~SofaStream.get_dimension` to get the
        size/value of a specific dimensions as integer number.

        The SOFA standard defines the following dimensions that are used
        to define the shape of the data entries:

        M
            number of measurements
        N
            number of samples, frequencies, SOS coefficients
            (depending on GLOBAL_DataType)
        R
            Number of receivers or SH coefficients
            (depending on ReceiverPosition_Type)
        E
            Number of emitters or SH coefficients
            (depending on EmitterPosition_Type)
        S
            Maximum length of a string in a string array
        C
            Size of the coordinate dimension. This is always three.
        I
            Single dimension. This is always one.

        """
        dim = self._file.dimensions

        # get verbose description for dimesion N
        if self._file.getncattr('DataType').startswith("FIR"):
            N_verbose = "samples"
        elif self._file.getncattr('DataType').startswith("TF"):
            N_verbose = "frequencies"
        elif self._file.getncattr('DataType').startswith("SOS"):
            N_verbose = "SOS coefficients"

        # get verbose description for dimensions R and E
        R_verbose = (
            "receiver spherical harmonics coefficients"
            if 'harmonic'
            in self._file.variables['ReceiverPosition'].getncattr('Type')
            else "receiver"
            )
        E_verbose = (
            "emitter spherical harmonics coefficients"
            if 'harmonic'
            in self._file.variables['EmitterPosition'].getncattr('Type')
            else "emitter"
            )

        dimensions = {
            "M": "measurements",
            "N": N_verbose,
            "R": R_verbose,
            "E": E_verbose,
            "S": "maximum string length",
            "C": "coordinate dimensions, fixed",
            "I": "single dimension, fixed"}

        info_str = ""
        for key, value in dim.items():
            value = value.size
            dim_info = dimensions[key] if key in dimensions \
                else "custom dimension"

            info_str += f"{key} = {value} {dim_info}" + '\n'

        print(info_str)

    def get_dimension(self, dimension):
        """
        Get size of a SOFA dimension.

        SOFA dimensions specify the shape of the data contained in a SOFA-file.
        For a list of all dimensions see :py:func:`~list_dimensions`, for more
        information about the data contained in a SOFA-file use
        :py:func:`~inspect`.

        Parameters
        ----------
        dimension : str
            The dimension as a string, e.g., ``'N'``.

        Returns
        -------
        size : int
            the size of the queried dimension.
        """

        # get dimensons from SOFA-file
        dims = self._file.dimensions

        if dimension not in dims.keys():
            raise ValueError((
                f"{dimension} is not a valid dimension. "
                "See Sofa.list_dimensions for a list of valid dimensions."))

        return dims[dimension].size

    def inspect(self, file=None):
        """
        Get information about the data inside a SOFA-file.

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
            for att_ in list(self._file[key].ncattrs()):
                info_str += (key.replace('.', '_') + f'_{att_} : '
                             + getattr(data, att_) + '\n')

        # write to text file
        if file is not None:
            with open(file, 'w') as f_id:
                f_id.write(info_str + "\n")

        # print to console
        print(info_str)
