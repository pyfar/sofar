import contextlib
import os
import numpy as np
from netCDF4 import Dataset, chartostring, stringtochar
import warnings
import pathlib
from packaging.version import parse
import sofar as sf
from .utils import _verify_convention_and_version, _atleast_nd


def read_sofa(filename, verify=True, verbose=True):
    """
    Read SOFA file from disk and convert it to SOFA object.

    Numeric data is returned as floats or numpy float arrays unless they have
    missing data, in which case they are returned as numpy masked arrays.

    Parameters
    ----------
    filename : str
        The full path to the sofa data.
    verify : bool, optional
        Verify and update the SOFA object by calling :py:func:`~Sofa.verify`.
        This helps to find potential errors in the default values and is thus
        recommended. If reading a file does not work, try to call `Sofa` with
        ``verify=False``. The default is ``True``.
    verbose : bool, optional
        Print the names of detected custom variables and attributes. The
        default is ``True``

    Returns
    -------
    sofa : Sofa
        Object containing the data from `filename`.

    Notes
    -----

    1. Missing dimensions are appended when writing the SOFA object to disk.
       E.g., if ``sofa.Data_IR`` is of shape (1, 2) it is written as an array
       of shape (1, 2, 1) because the SOFA standard AES69-2020 defines it as a
       three dimensional array with the dimensions (`M: measurements`,
       `R: receivers`, `N: samples`)
    2. When reading data from a SOFA file, array data is always returned as
       numpy arrays and singleton trailing dimensions are discarded (numpy
       default). I.e., ``sofa.Data_IR`` will again be an array of shape (1, 2)
       after writing and reading to and from disk.
    3. One dimensional arrays with only one element will be converted to scalar
       values. E.g. ``sofa.Data_SamplingRate`` is stored as an array of shape
       (1, ) inside SOFA files (according to the SOFA standard AES69-2020) but
       will be a scalar inside SOFA objects after reading from disk.
    """

    return _read_netcdf(filename, verify, verbose, mode="sofa")


def read_sofa_as_netcdf(filename):
    """
    Read corrupted SOFA data from disk.

    .. note::
        `read_sofa_as_netcdf` is intended to read and fix corrupted SOFA data
        that could not be read by :py:func:`~read_sofa`. The recommend workflow
        is

        - Try to read the data with `read_sofa` and ``verify=True``
        - If this fails, try the above with ``verify=False``
        - If this fails, use `read_sofa_as_netcdf`

        The SOFA object  returned by `read_sofa_as_netcdf` may not work
        correctly before the issues with the data were fixed, i.e., before the
        data are in agreement with the SOFA standard AES-69.

    Numeric data is returned as floats or numpy float arrays unless they have
    missing data, in which case they are returned as numpy masked arrays.

    Parameters
    ----------
    filename : str
        The full path to the NetCDF data.

    Returns
    -------
    sofa : Sofa
        Object containing the data from `filename`.

    Notes
    -----

    1. Missing dimensions are appended when writing the SOFA object to disk.
       E.g., if ``sofa.Data_IR`` is of shape (1, 2) it is written as an array
       of shape (1, 2, 1) because the SOFA standard AES69-2020 defines it as a
       three dimensional array with the dimensions (`M: measurements`,
       `R: receivers`, `N: samples`)
    2. When reading data from a SOFA file, array data is always returned as
       numpy arrays and singleton trailing dimensions are discarded (numpy
       default). I.e., ``sofa.Data_IR`` will again be an array of shape (1, 2)
       after writing and reading to and from disk.
    3. One dimensional arrays with only one element will be converted to scalar
       values. E.g. ``sofa.Data_SamplingRate`` is stored as an array of shape
       (1, ) inside SOFA files (according to the SOFA standard AES69-2020) but
       will be a scalar inside SOFA objects after reading from disk.
    """
    return _read_netcdf(filename, False, False, mode="netcdf")


def _read_netcdf(filename, verify, verbose, mode):

    # check the filename
    filename = pathlib.Path(filename).with_suffix('.sofa')
    if not os.path.isfile(filename):
        raise ValueError(f"{filename} does not exist")

    # attributes that are skipped
    skip = ["_Encoding"]

    # init list of all and custom attributes
    all_attr = []
    custom = []

    # open new NETCDF4 file for reading
    with Dataset(filename, "r", format="NETCDF4") as file:

        if mode == "sofa":
            # get convention name and version
            convention = getattr(file, "SOFAConventions")
            version = getattr(file, "SOFAConventionsVersion")

            # check if convention and version exist
            _verify_convention_and_version(version, convention)

            # get SOFA object with default values
            sofa = sf.Sofa(convention, version=version, verify=verify)
        else:
            sofa = sf.Sofa(None)

        # allow writing read only attributes
        sofa.protected = False

        # load global attributes
        for attr in file.ncattrs():

            value = getattr(file, attr)
            all_attr.append(f"GLOBAL_{attr}")

            if not hasattr(sofa, f"GLOBAL_{attr}"):
                sofa._add_custom_api_entry(
                    f"GLOBAL_{attr}", value, None, None, "attribute")
                custom.append(f"GLOBAL_{attr}")
                sofa.protected = False
            else:
                setattr(sofa, f"GLOBAL_{attr}", value)

        # load data
        for var in file.variables.keys():

            value = _format_value_from_netcdf(file[var][:], var)
            all_attr.append(var.replace(".", "_"))

            if hasattr(sofa, var.replace(".", "_")):
                setattr(sofa, var.replace(".", "_"), value)
            else:
                dimensions = "".join(list(file[var].dimensions))
                # SOFA only uses dtypes 'double' and 'S1' but netCDF has more
                dtype = "string" if file[var].datatype == "S1" else "double"
                sofa._add_custom_api_entry(var.replace(".", "_"), value, None,
                                           dimensions, dtype)
                custom.append(var.replace(".", "_"))
                sofa.protected = False

            # load variable attributes
            for attr in [a for a in file[var].ncattrs() if a not in skip]:

                value = getattr(file[var], attr)
                all_attr.append(var.replace(".", "_") + "_" + attr)

                if not hasattr(sofa, var.replace(".", "_") + "_" + attr):
                    sofa._add_custom_api_entry(
                        var.replace(".", "_") + "_" + attr, value, None,
                        None, "attribute")
                    custom.append(var.replace(".", "_") + "_" + attr)
                    sofa.protected = False
                else:
                    setattr(sofa, var.replace(".", "_") + "_" + attr, value)

    # remove fields from initial Sofa object that were not contained in NetCDF
    # file (initial Sofa object contained mandatory and optional fields)
    attrs = [attr for attr in sofa.__dict__.keys() if not attr.startswith("_")]
    for attr in attrs:
        if attr not in all_attr:
            delattr(sofa, attr)

    # do not allow writing read only attributes any more
    sofa.protected = True

    # notice about custom entries
    if custom and verbose:
        print(("SOFA file contained custom entries\n"
               "----------------------------------\n"
               f"{', '.join(custom)}"))

    # update api
    if verify:
        try:
            sofa.verify(mode="read")
        except: # noqa (No error handling - just improved verbosity)
            raise ValueError((
                "The SOFA object could not be verified, maybe due to erroneous"
                " data. Call sofa=sofar.read_sofa(filename, verify=False) and "
                "then sofa.verify() to get more information"))

    return sofa


def write_sofa(filename: str, sofa: sf.Sofa, compression=4):
    """
    Write a SOFA object to disk as a SOFA file.

    Parameters
    ----------
    filename : str
        The filename. '.sofa' is appended to the filename, if it is not
        explicitly given.
    sofa : object
        The SOFA object that is written to disk
    compression : int
        The level of compression with ``0`` being no compression and ``9``
        being the best compression. The default of ``9`` optimizes the file
        size but increases the time for writing files to disk.

    Notes
    -----

    1. Missing dimensions are appended when writing the SOFA object to disk.
       E.g., if ``sofa.Data_IR`` is of shape (1, 2) it is written as an array
       of shape (1, 2, 1) because the SOFA standard AES69-2020 defines it as a
       three dimensional array with the dimensions (`M: measurements`,
       `R: receivers`, `N: samples`)
    2. When reading data from a SOFA file, array data is always returned as
       numpy arrays and singleton trailing dimensions are discarded (numpy
       default). I.e., ``sofa.Data_IR`` will again be an array of shape (1, 2)
       after writing and reading to and from disk.
    3. One dimensional arrays with only one element will be converted to scalar
       values. E.g. ``sofa.Data_SamplingRate`` is stored as an array of shape
       (1, ) inside SOFA files (according to the SOFA standard AES69-2020) but
       will be a scalar inside SOFA objects after reading from disk.
    """
    _write_sofa(filename, sofa, compression, verify=True)


def _write_sofa(filename: str, sofa: sf.Sofa, compression=4, verify=True):
    """
    Private write function for writing invalid SOFA files for testing. See
    write_sofa for documentation.
    """

    # check the filename
    filename = pathlib.Path(filename).with_suffix('.sofa')

    if verify:
        # check if the latest version is used for writing and warn otherwise
        # if case required for writing SOFA test data that violates the
        # conventions
        if sofa.GLOBAL_SOFAConventions != "invalid-value":
            latest = sf.Sofa(sofa.GLOBAL_SOFAConventions)
            latest = latest.GLOBAL_SOFAConventionsVersion
            current = sofa.GLOBAL_SOFAConventionsVersion

            if parse(current) < parse(latest):
                warnings.warn((
                    "Writing SOFA object with outdated Convention "
                    f"version {current}. It is recommend to upgrade "
                    " data with Sofa.upgrade_convention() before "
                    "writing to disk if possible."))

    # setting the netCDF compression parameter
    use_zlib = compression != 0

    # update the dimensions
    if verify:
        sofa.verify(mode="write")

    # list of all attribute names
    all_keys = [key for key in sofa.__dict__.keys() if not key.startswith("_")]

    # open new NETCDF4 file for writing
    with Dataset(filename, "w", format="NETCDF4") as file:

        # write dimensions
        for dim in sofa._api:
            file.createDimension(dim, sofa._api[dim])

        # write global attributes
        keys = [key for key in all_keys if key.startswith("GLOBAL_")]
        for key in keys:
            setattr(file, key[7:], str(getattr(sofa, key)))

        # write data
        for key in all_keys:

            # skip attributes
            # Note: This definition of attribute is blurry:
            # lax definition:
            #   sofa._convention[key]["type"] == "attribute":
            # strict definition:
            #   ("_" in key and not key.startswith("Data_")) or \
            #       key.count("_") > 1
            #
            # The strict definition is implicitly included in the SOFA standard
            # since underscores only occur for variables starting with Data_
            if sofa._convention[key]["type"] == "attribute":
                continue

            # get the data and type and shape
            value, dtype = _format_value_for_netcdf(
                getattr(sofa, key), key, sofa._convention[key]["type"],
                sofa._dimensions[key], sofa._api["S"])

            # create variable and write data
            shape = tuple(list(sofa._dimensions[key]))
            tmp_var = file.createVariable(
                key.replace("Data_", "Data."), dtype, shape,
                zlib=use_zlib, complevel=compression)
            if dtype == "f8":
                tmp_var[:] = value
            else:
                tmp_var[:] = stringtochar(value)
                tmp_var._Encoding = "ascii"

            # write variable attributes
            sub_keys = [k for k in all_keys if k.startswith(f"{key}_")]
            for sub_key in sub_keys:
                setattr(tmp_var, sub_key[len(key)+1:],
                        str(getattr(sofa, sub_key)))


def _format_value_for_netcdf(value, key, dtype, dimensions, S):
    """
    Format value from SOFA object for saving in a NETCDF4 file.

    Parameters
    ----------
    value : str, array like
        The value to be formatted
    key : str
        The name of the current attribute. Needed for verbose errors.
    dtype : str
        The the data type of value
    dimensions : str
        The intended dimensions from ``sofa.dimensions``
    S : int
        Length of the string array.

    Returns
    -------
    value : str, numpy array
        The formatted value.
    netcdf_dtype : str
        The data type as a string for writing to a NETCDF4 file ('attribute',
        'f8', or 'S1').
    """
    # copy value
    with contextlib.suppress(AttributeError):
        value = value.copy()

    # parse data
    if dtype == "attribute":
        value = str(value)
        netcdf_dtype = "attribute"
    elif dtype == "double":
        value = _atleast_nd(value, len(dimensions))
        netcdf_dtype = "f8"
    elif dtype == "string":
        value = np.array(value, dtype=f"S{str(S)}")
        value = _atleast_nd(value, len(dimensions))
        netcdf_dtype = 'S1'
    else:
        raise ValueError(f"Unknown type {dtype} for {key}")

    return value, netcdf_dtype


def _format_value_from_netcdf(value, key):
    """
    Format value from NETCDF4 file for saving in a SOFA object

    Parameters
    ----------
    value : np.array of dtype float or S
        The value to be formatted
    key : str
        The variable name of the current value. Needed for verbose errors.

    Returns
    -------
    value : str, number, numpy array
        The formatted value.
    """

    if "float" in str(value.dtype) or "int" in str(value.dtype):
        if np.ma.is_masked(value):
            warnings.warn(f"Entry {key} contains missing data")
        else:
            # Convert to numpy array or scalar
            value = np.asarray(value)
    elif str(value.dtype)[1] in ["S", "U"]:
        # string arrays are stored in masked arrays with empty strings '' being
        # masked. Convert to regular arrays with unmasked empty strings
        if str(value.dtype)[1] == "S":
            value = chartostring(value, encoding="ascii")
        value = np.atleast_1d(value).astype("U")
    else:
        raise TypeError(
            f"{key}: value.dtype is {value.dtype} but must be float, S or, U")

    # convert arrays to scalars if they do not store data that is usually used
    # as scalar metadata, e.g., the SamplingRate
    data_keys = ["Data_IR", "Data_Real", "Data_Imag", "Data_SOS" "Data_Delay"]
    if value.size == 1 and key not in data_keys:
        value = value[0]

    return value
