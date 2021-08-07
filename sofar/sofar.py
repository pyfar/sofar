import os
import glob
import json
import requests
from datetime import datetime
import platform
import numpy as np
import numpy.testing as npt
import warnings
from bs4 import BeautifulSoup
from netCDF4 import Dataset
import sofar as sf


def update_conventions():
    """
    Update SOFA conventions.

    A SOFA convention defines the kind of data and the data format that is
    stored in a SOFA file. Updating the conventions is done in two steps:

    1.
        Download official SOFA conventions as csv files from
        https://github.com/sofacoustics/API_MO/tree/master/API_MO/conventions.
    2.
        Convert csv files to json files for easier handling

    The csv and json files are stored at sofar/conventions. Sofar works only on
    the json files. To get a list of all currently available SOFA conventions
    and their paths see :py:func:`~sofar.list_conventions`.
    """

    # url for parsing and downloading the convention files
    url = ("https://github.com/sofacoustics/API_MO/tree/"
           "master/API_MO/conventions")
    url_raw = ("https://raw.githubusercontent.com/sofacoustics/API_MO/"
               "master/API_MO/conventions")
    ext = 'csv'

    print(f"Downloading and converting SOFA conventions from {url} ...")

    # get file names of conventions from the SOFA Matlab/Octave API
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    conventions = [os.path.split(node.get('href'))[1]
                   for node in soup.find_all('a')
                   if node.get('href').endswith(ext)]

    # Loop conventions
    for convention in conventions:

        # exclude these conventions
        if convention.startswith(("General_", "GeneralString_")):
            continue

        filename_csv = os.path.join(
            os.path.dirname(__file__), "conventions", convention)
        filename_json = filename_csv[:-3] + "json"

        # download SOFA convention definitions to package diretory
        data = requests.get(url_raw + "/" + convention)
        with open(filename_csv, "wb") as file:
            file.write(data.content)

        # convert SOFA conventions from csv to json
        convention_dict = _convention_csv2dict(filename_csv)

        with open(filename_json, 'w') as file:
            json.dump(convention_dict, file)

    print("... done.")


def list_conventions(verbose=True, return_type=None):
    """
    List available SOFA conventions.

    Parameters
    ----------
    verbose=True : bool, optional
        Print the names and versions of the currently supported conventions to
        the console. The default is ``True``.
    return_type : string, optional
        ``'path'``
            Return a list with the full paths and filenames of the convention
            files
        ``'name'``
            Return a list of the convention names without version
        ``'name_version'``
            Return a list of tuples containing the convention name and version.

        The default is ``None`` which does not return anything

    Returns
    -------
    See parameter `return_type`.
    """
    # directory containing the SOFA conventions
    directory = os.path.join(os.path.dirname(__file__), "conventions")

    # SOFA convention files
    paths = [file for file in glob.glob(os.path.join(directory, "*.json"))]

    if verbose:
        print("Available SOFA conventions:")

    conventions = []
    versions = []
    for path in paths:
        fileparts = os.path.basename(path).split(sep="_")
        conventions += [fileparts[0]]
        versions += [fileparts[1][:-5]]
        if verbose:
            print(f"{conventions[-1]} (Version {versions[-1]})")

    if return_type is None:
        return
    if return_type == "path":
        return paths
    elif return_type == "name":
        return conventions
    elif return_type == "name_version":
        return [(n, v) for n, v in zip(conventions, versions)]


def create_sofa(convention, mandatory=False, version="latest"):
    """Create and empty SOFA file.

    Parameters
    ----------
    convention : str
        The name of the convention from which the SOFA file is created. See
        :py:func:`~sofar.list_conventions`.
    mandatory : bool, optional
        If ``True``, only the mandatory fields of the convention will be
        returned. The default is ``False``, which returns mandatory and
        optional fields.
    version : str, optional
        The version of the convention as a string, e.g., ``' 2.0'``. The
        default is ``'latest'``. Also see :py:func:`~sofar.list_conventions`.

    Returns
    -------
    sofa : dict
        The SOFA dictionairy filled with the default values of the convention.
    """

    # get convention
    convention = _load_convention(convention, version)
    # convert convention to SOFA file in dict format
    sofa = _convention2sofa(convention, mandatory)
    # add and update the API
    update_api(sofa, version)

    return sofa


def set_value(sofa, key, value):
    """
    Set value specified by the key in a SOFA file.

    Parameters
    ----------
    sofa : dict
        A SOFA dictionairy obtained from :py:func:`~sofar.create_sofa` or
        :py:func:`~sofar.read_sofa`.
    key : str, list of strings
        The name of the attribute to which the value is assigned, i.e.,
        ``'ListenerPosition'``, or ``['Data', 'IR']``.
    value : number, string, list, array
        The value to be assigned.

    Retruns
    -------
    The value is updated in `sofa` without the need for returning it. This
    is because Python dictionaries are mutable objects, i.e., changes inside
    this function also change the object outside.
    """

    # check the key
    if key not in sofa.keys():
        raise ValueError(f"'{key}' is an invalid key")
    if key == "API" or "r" in sofa["API"]["Convention"][key]["flags"]:
        raise ValueError(f"'{key}' is read only")

    # check if the value has to be converted
    dimensions = sofa["API"]["Convention"][key]["dimensions"]
    if dimensions is not None:
        ndim = len(dimensions.split(", ")[0])
        value = _nd_array(value, ndim)

    # set the value
    sofa[key] = value


def update_api(sofa, version="latest"):
    """
    Update the API of a SOFA dictionary.

    Update the API, check if all mandatory fields are contained and if the
    dimensions of the data inside the SOFA dictionary are consistent. If a
    mandatory field is missing, it is added to the SOFA dictionary with its
    default value and a warning is raised.

    sofa['API'] contains metadata that is by :py:func:`~sofar.write_sofa` for
    writing the SOFA dictionary to disk. The API contains the following fields:

    'Convention'
        The SOFA convention with default values, variable dimensions, flags and
        comments
    'Dimensions'
        The detected dimensions of the data inside the SOFA dictionairy
    'R', 'E', 'M', 'N', 'C', 'I', 'S'
        The size of the dimensions. This specifies the dimensions of the data
        inside the SOFA dictionary.

    Parameters
    ----------
    sofa : dict
        The data as a SOFA dictionary (as returned by
        :py:func:`~sofar.create_sofa` and :py:func:`~sofar.read_sofa`)
    version : str, optional
        The version to which the API is updated.

        ``'latest'``
            Use the latest API and upgrade the SOFA file if required.
        ``'match'``
            Match the version of the sofa file.
        str
            Version string, e.g., ``'1.0'``. Note that this might downgrade
            the SOFA dictionairy

        The default is ``'latest'``

    Returns
    -------
    The values are updated in `sofa` without the need for returning it. This
    is because Python dictionaries are mutable objects. Lists are converted
    to numpy arrays.

    Notes
    -----
    :py:func:`~sofar.write_sofa` also calls `update_api`. This function does
    thus not have to be called before using `write_sofa`.
    """

    # initialize the API
    _add_api(sofa, version)
    sofa["API"]["Dimensions"] = {}

    # get all keys that have a dimension and exclude the API
    keys = [key for key in sofa.keys()
            if key != "API"
            and sofa["API"]["Convention"][key]["dimensions"] is not None]

    # first run: check if the mandatory fields are contained
    for key in sofa["API"]["Convention"].keys():
        if _is_mandatory(sofa["API"]["Convention"][key]["flags"]) \
                and key not in keys:
            sofa[key] = sofa["API"]["Convention"][key]["default"]
            warnings.warn((
                f"Mandatory field {key} was missing and added to the SOFA "
                "dictionairy with its default value"))

    # second run: Get the dimensions for E, R, M, N, and S
    S = 0
    for key in keys:

        value = sofa[key]
        dimensions = sofa["API"]["Convention"][key]["dimensions"]

        for id, dim in enumerate(dimensions.split(", ")[0]):
            if dim in "ermn":
                sofa["API"][dim.upper()] = \
                    _nd_array(value, 4).shape[id]
            if dim == "S":
                S = max(S, _get_size_and_shape_of_string_var(value, key)[0])

    # add fixed sizes
    sofa["API"]["C"] = 3
    sofa["API"]["I"] = 1
    sofa["API"]["S"] = S

    # third run: verify dimensions of data
    for key in keys:

        # handle dimensions
        dimensions = sofa["API"]["Convention"][key]["dimensions"]

        # get value and actual shape
        try:
            value = sofa[key].copy()
        except AttributeError:
            value = sofa[key]

        if "S" in dimensions:
            # string or string array like data
            shape_act = _get_size_and_shape_of_string_var(value, key)[1]
        else:
            # array like data
            shape_act = _nd_array(value, 4).shape

        shape_matched = False
        for dim in dimensions.split(", "):

            # get the reference shape ('S' translates to a shape of 1, because
            # the strings are stored in an array whose shape does not reflect
            # the max. lengths of the actual strings inside it)
            shape_ref = tuple(
                [sofa["API"][d.upper()] if d != "S" else 1 for d in dim])

            # get shape for comparison to correct length by cropping and
            # appending singelton dimensions if required
            shape_compare = shape_act[:len(shape_ref)]
            for _ in range(len(shape_ref) - len(shape_compare)):
                shape_compare += (1, )

            # check if the shapes match and write to API
            if shape_compare == shape_ref:
                shape_matched = True
                sofa["API"]["Dimensions"][key] = dim.upper()
                break

        if not shape_matched:
            raise ValueError(
                (f"The shape of {key} is {shape_compare} but has "
                 f"to be: {dimensions.upper()} "
                 "(see field 'API' in the SOFA file)"))


def read_sofa(filename, update=True, version="latest"):
    """
    Read SOFA file from disk and convert it to SOFA dictionairy.

    Numeric data is returned as floats or numpy float arrays unless they have
    missing data, in which case they are returned as numpy masked arrays.

    Parameters
    ----------
    filename : str
        The filename. '.sofa' is appended to the filename, if it is not
        explicitly given.
    update : bool, optional
        Update the API by calling :py:func:`~sofar.update_api`. This helps
        to find potential errors in the data and is thus recommended. If
        reading a file does not work, try to call `read_sofa` with
        ``update=False``. The default is ``True``.
    version : str, optional
        The version to which the API is updated.

        ``'latest'``
            Use the latest API and upgrade the SOFA file if required.
        ``'match'``
            Match the version of the sofa file.
        str
            Version string, e.g., ``'1.0'``. Note that this might downgrade
            the SOFA dictionairy

        The default is ``'latest'``

    Returns
    -------
    sofa : dict
        The SOFA dictionairy filled with the default values of the convention.
    """

    # check the filename
    if not filename.lower().endswith('.sofa'):
        filename += ".sofa"
    if not os.path.isfile(filename):
        raise ValueError("{filename} does not exist")

    # init SOFA dictionairy
    sofa = {}

    # open new NETCDF4 file for reading
    with Dataset(filename, "r", format="NETCDF4") as file:

        # load global attributes
        for attr in file.ncattrs():
            sofa["GLOBAL:" + attr] = getattr(file, attr)

        # load data
        for var in file.variables.keys():
            # format and write value
            value = _format_value_from_netcdf(file[var][:], var)
            sofa[var] = value

            # load variable attributes
            for attr in file[var].ncattrs():
                sofa[var + ":" + attr] = getattr(file[var], attr)

    # update api
    if update:
        try:
            update_api(sofa, version)
        except: # noqa (No error handling - just improved verbosity)
            raise ValueError((
                "The API could not be updated, maybe do to errornous data in "
                "the SOFA file. Tr to call sofa=sofar.read_sofa(filename, "
                "update=False) and than call sofar.update_api(sofa) to get "
                "more informations"))

    return sofa


def write_sofa(filename: str, sofa: dict, version="latest"):
    """
    Write a SOFA dictionary to disk as a SOFA file.

    Parameters
    ----------
    filename : str
        The filename. '.sofa' is appended to the filename, if it is not
        explicitly given.
    sofa : dict
        The SOFA dictionairy that is written to disk

    Returns
    -------
    This function calls :py:func:`~sofar.update_api` before writing to disk.
    The API is updated in `sofa` without the need for returning it. This
    is because Python dictionaries are mutable objects, i.e., changes inside
    this function also change the object outside.
    """

    # check the filename
    if not filename.lower().endswith('.sofa'):
        filename += ".sofa"

    # update the dimensions
    update_api(sofa, version)

    # open new NETCDF4 file for writing
    with Dataset(filename, "w", format="NETCDF4") as file:

        # write dimensions
        for dim in sofa["API"]:
            # Dimensions are stored in single upper case letter keys
            if len(dim) == 1:
                file.createDimension(dim, sofa["API"][dim])

        # write global attributes
        keys = [key for key in sofa.keys() if key.startswith("GLOBAL:")]
        for key in keys:
            setattr(file, key[7:], str(sofa[key]))

        # write data
        keys = [key for key in sofa.keys() if ":" not in key and key != "API"]
        for key in keys:

            # get the data and type and shape
            value, dtype = _format_value_for_netcdf(
                sofa[key], key, sofa["API"]["Dimensions"][key],
                sofa["API"]["S"])

            # create variable and write data
            shape = tuple([dim for dim in sofa["API"]["Dimensions"][key]])
            tmp_var = file.createVariable(key, dtype, shape)
            try:
                tmp_var[:] = value
            except: # noqa (this is no error handling just improved verbosity)
                shape_verbose = []
                for dim in sofa["API"]["Dimensions"][key]:
                    shape_verbose = shape_verbose.append(
                        dim + "=" + str(sofa["API"][dim]))

                raise ValueError((
                    f"Error writing sofa['{key}']: {value} of "
                    f"intended type '{dtype}' and shape {shape_verbose}"))

            # write variable attributes
            sub_keys = [k for k in sofa.keys() if k.startswith(key + ":")]
            for sub_key in sub_keys:
                setattr(tmp_var, sub_key[len(key)+1:], str(sofa[sub_key]))


def info(sofa, info="summary"):
    """
    Print information about a SOFA dictionariy

    Parameters
    ----------
    sofa : dict
        A SOFA dictionairy.
    info : str
        Specifies the kind of information that is printed:

        ``'summary'``
            Print general information about the SOFA dictionairy
        ``'keys'``
            Print the name of all keys
        ``'mandatory'``
            Print all mandatory keys
        ``'optional'``
            Print all optional keys
        ``'dimensions'``
            Print the dimensions
        ``'comments'``
            Print the explanatory comments
        ``'defaults'``
            Print the default values

        The dimensions comments and defaults can be printed for specific keys,
        e.g., ``'dimensions:Data.IR'`` will only print the dimensions for a
        single key, while ``'dimensions.Data'`` will print the dimensions for
        multiple keys because the term `Data` occurs more than once.

    """
    pass


def compare_sofa(sofa_a, sofa_b, verbose=True, exclude=None):
    """
    Compare two sofa files against each other

    Parameters
    ----------
    sofa_a : dict
        SOFA dictionairy
    sofa_b : dict
        SOFA dictionairy
    verbose : bool, optional
        Print to console if differences were found. The default is True.
    exclude : str, optional
        Specify what fields should be excluded from the comparison

        ``'GLOBAL'``
            Exclude all global attributes, i.e., fields starting with 'GLOBAL:'
        ``'DATE'``
            Exclude date attributs, i.e., fields that contain 'Date'
        ``'ATTR'``
            Exclude all attributes, i.e., fields that contain ':'

        The default is None, which does not exclude anything.

    Returns
    -------
    is_identical : bool
        True if sofa_a and sofa_b are identical, False otherwise.
    """

    is_identical = True

    # set filter for excluding keys
    if exclude is not None:
        if exclude.upper() == "GLOBAL":
            exclude = "GLOBAL:"
        elif exclude.upper() == "ATTR":
            exclude = ":"
        elif exclude.upper() != "DATE":
            raise ValueError(
                f"exclude is {exclude} but must be GLOBAL, DATE, or ATTR")

    # get the keys
    if exclude is not None:
        keys_a = [k for k in sofa_a.keys() if k != "API" and exclude not in k]
        keys_b = [k for k in sofa_b.keys() if k != "API" and exclude not in k]
    else:
        keys_a = [k for k in sofa_a.keys() if k != "API"]
        keys_b = [k for k in sofa_b.keys() if k != "API"]

    # check for equal length
    if len(keys_a) != len(keys_b):
        is_identical = False
        if verbose:
            warnings.warn((f"not identical: sofa_a has {len(keys_a)} entries "
                           f"and sofa_b {len(keys_b)}."))

        return is_identical

    # check if the keys match
    if set(keys_a) != set(keys_b):
        is_identical = False
        if verbose:
            warnings.warn(
                "not identical: sofa_a and sofa_b do not have the same keys")

        return is_identical

    # compare attributes
    for key in [k for k in keys_a if ":" in k]:

        if sofa_a[key] != sofa_b[key]:
            is_identical = False
            if verbose:
                warnings.warn(
                    f"not identical: different values for {key}")

    # compare data
    for key in [k for k in keys_a if ":" not in k]:

        # get the values and copy them to avoid changing mutable objects
        a = sofa_a[key]
        b = sofa_b[key]
        try:
            a = a.copy()
            b = b.copy()
        except AttributeError:
            pass

        currently_identical = True

        # This is a bit messy because the comparison depends on the data type.
        # Does anyone have a better idea?
        if isinstance(a, (int, float, complex, str)) \
                and isinstance(b, (int, float, complex, str)):
            if a != b:
                currently_identical = False
        elif isinstance(a, np.ndarray) and isinstance(a, np.ndarray):
            if str(a.dtype).startswith("<U") or str(b.dtype).startswith("<U"):
                if not np.all(np.squeeze(a) == np.squeeze(b)):
                    currently_identical = False
            else:
                if npt.assert_allclose(np.squeeze(a), np.squeeze(b)):
                    currently_identical = False
        elif isinstance(a, (list, tuple, np.ndarray)) \
                and isinstance(b, (list, tuple, np.ndarray)):
            if npt.assert_allclose(np.squeeze(a), np.squeeze(b)):
                currently_identical = False
        elif isinstance(a, str) or isinstance(b, str):
            if not np.all(np.squeeze(a) == np.squeeze(b)):
                currently_identical = False
        else:
            try:
                if not np.all(np.squeeze(a) == np.squeeze(b)):
                    currently_identical = False
            except: # noqa (not a real exception, only more verbose feedback)
                is_identical = False
                warnings.warn(
                    f"not identical: data types of {key} could not be matched")

        if not currently_identical:
            is_identical = False
            if verbose:
                warnings.warn(
                    f"not identical: different values for {key}")

    return is_identical


def _convention_csv2dict(file: str):
    """
    Read SOFA convention from csv file and convert to json file. The csv files
    are taken from the official Matlab/Octave SOFA API.

    Parameters
    ----------
    file : str
        filename of the SOFA convention

    Returns
    -------
    convention : dict
        SOFA convention as nested dictionary. Each attribute is a sub
        dictionary with the keys `default`, `flags`, `dimensions`, `type`, and
        `comment`.
    """

    # read the file
    with open(file, 'r') as fid:
        lines = fid.readlines()

    # write into dict
    convention = {}
    for idl, line in enumerate(lines):

        try:
            # separate by tabs
            line = line.strip().split("\t")
            # parse the line entry by entry
            for idc, cell in enumerate(line):
                # detect empty cells and leading trailing white spaces
                cell = None if cell.replace(' ', '') == '' else cell.strip()
                # nothing to do for empty cells
                if cell is None:
                    line[idc] = cell
                    continue
                # parse text cells that do not contain arrays
                if cell[0] != '[':
                    # check for numbers
                    try:
                        cell = float(cell) if '.' in cell else int(cell)
                    except ValueError:
                        pass

                    line[idc] = cell
                    continue

                # parse array cell
                # remove brackets
                cell = cell[1:-1]

                if ';' not in cell:
                    # get rid of white spaces
                    cell = cell.strip()
                    cell = cell.replace(' ', ',')
                    cell = cell.replace(' ', '')
                    # create flat list of integers and floats
                    numbers = cell.split(',')
                    cell = [float(n) if '.' in n else int(n) for n in numbers]
                else:
                    # create a nested list of integers and floats
                    # separate multidimensional arrays
                    cell = cell.split(';')
                    cell_nd = [None] * len(cell)
                    for idx, cc in enumerate(cell):
                        # get rid of white spaces
                        cc = cc.strip()
                        cc = cc.replace(' ', ',')
                        cc = cc.replace(' ', '')
                        numbers = cc.split(',')
                        cell_nd[idx] = [float(n) if '.' in n else int(n)
                                        for n in numbers]

                    cell = cell_nd

                # write parsed cell to line
                line[idc] = cell

            # first line contains field names
            if idl == 0:
                fields = line[1:]
                continue

            # add blank comment if it does not exist
            if len(line) == 5:
                line.append("")
            # convert empty defaults from None to ""
            if line[1] is None:
                line[1] = ""

            # make sure some unusual default values are converted for json
            if line[1] == "permute([0 0 0 1 0 0; 0 0 0 1 0 0], [3 1 2]);":
                # Field Data.SOS in SimpleFreeFieldHRSOS and SimpleFreeFieldSOS
                line[1] = [[[0, 0, 0, 1, 0, 0], [0, 0, 0, 1, 0, 0]]]
            if line[1] == "{''}":
                line[1] = ['']

            # write second to last line
            convention[line[0]] = {}
            for ff, field in enumerate(fields):
                convention[line[0]][field.lower()] = line[ff + 1]

        except: # noqa
            raise ValueError((f"Failed to parse line {idl}, entry {idc} in: "
                              f"{file}: \n{line}\n"))

    # reorder the fields to be nicer to read and understand
    # 1. Move everything to the end that is not GLOBAL
    keys = [key for key in convention.keys()]
    for key in keys:
        if "GLOBAL" not in key:
            convention[key] = convention.pop(key)
    # 1. Move Data entries to the end
    for key in keys:
        if key.startswith("Data"):
            convention[key] = convention.pop(key)

    return convention


def _load_convention(convention, version):
    """
    Load SOFA convention from json file.

    Parameters
    ----------
    convention : str
        The name of the convention from which the SOFA file is created. See
        :py:func:`~sofar.list_conventions`.

    Returns
    -------
    convention : dict
        The SOFA convention as a dictionary object
    """
    # check input
    if not isinstance(convention, str):
        raise TypeError(
            f"Convention must be a string but is of type {type(convention)}")

    # get and check path to json file
    paths = list_conventions(False, "path")
    path = [path for path in paths
            if os.path.basename(path).startswith(convention + "_")]

    if not len(path):
        raise ValueError(
            (f"Convention '{convention}' not found. See "
             "sofar.list_conventions() for available conventions."))

    # select the correct version
    if version == "latest":
        path = path[-1]
    else:
        versions = [p.split('_')[1][:-5] for p in path]
        if version not in versions:
            raise ValueError((
                f"Version {version} not found. "
                f"Available versions are {versions}"))
        path = path[versions.index(version)]

    # read convention from json file
    with open(path, "r") as file:
        convention = json.load(file)

    return convention


def _convention2sofa(convention, mandatory):
    """
    Convert a SOFA convention to a SOFA file filled with the default values.

    Parameters
    ----------
    convention : dict
        The SOFA convention
    mandatory : bool
        Flag to indicate if only mandatory fields are included in the SOFA file

    Returns
    -------
    sofa : dict
        The SOFA file with default values
    """

    # initialize SOFA file
    sofa = {}

    # populate the SOFA file
    for key in convention.keys():

        # skip optional fields if requested
        if not _is_mandatory(convention[key]["flags"]) and mandatory:
            continue

        # set the default value
        default = convention[key]["default"]
        if isinstance(default, list):
            ndim = len(convention[key]["dimensions"].split(", ")[0])
            default = _nd_array(default, ndim)
        sofa[key] = default

    # write API and date specific read only fields
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    defaults = (["GLOBAL:DateCreated", now],
                ["GLOBAL:DateModified", now],
                ["GLOBAL:APIName", "sofar SOFA API for Python (pyfar.org)"],
                ["GLOBAL:APIVersion", sf.__version__],
                ["GLOBAL:ApplicationName", "Python"],
                ["GLOBAL:ApplicationVersion", platform.python_version()])
    for default in defaults:
        if default[0] in sofa:
            sofa[default[0]] = default[1]

    return sofa


def _add_api(sofa, version):
    """
    Add API to SOFA file. If The SOFA files contains an API it is overwritten.

    The API is basically the convention file, which holds the meta data that is
    required for writing the SOFA file to disk. It is added under sofa['API'].

    Parameters
    ----------
    sofa : dict
        The SOFA file without API
    version : str
        ``'latest'``
            Use the latest API and upgrade the SOFA file if required.
        ``'match'``
            Match the version of the sofa file.
        str
            Version string, e.g., ``'1.0'``.

    Returns
    -------
    sofa : dict
        The SOFA file with API
    """

    # load the desired convention and compare versions
    v_current = str(float(sofa["GLOBAL:SOFAConventionsVersion"]))
    if version == "match":
        version = v_current

    convention = _load_convention(sofa["GLOBAL:SOFAConventions"], version)
    v_new = str(float(convention["GLOBAL:SOFAConventionsVersion"]["default"]))

    if v_current != v_new:
        sofa["GLOBAL:SOFAConventionsVersion"] = float(v_new)

    if float(v_current) < float(v_new):
        warnings.warn(
            f"Upgraded SOFA dictionairy from version {v_current} to {v_new}")
    elif float(v_current) > float(v_new):
        warnings.warn(
            f"Downgraded SOFA dictionairy from version {v_current} to {v_new}")

    # add SOFA API
    sofa["API"] = {}
    sofa["API"]["Convention"] = convention


def _format_value_for_netcdf(value, key, dimensions, S):
    """
    Format value from SOFA dictionary for saving in a NETCDF4 file.

    Parameters
    ----------
    value : str, array like
        The value to be formatted
    key : str
        The variable name of the current value. Needed for verbose errors.
    dimensions : str
        The intended dimensions from sofa['API']['Dimensions']
    S : int
        Length of the string array.

    Returns
    -------
    value : str, numpy array
        The formatted value.
    netcdf_dtype : str
        The data type as a string for writing to a NETCDF4 file.
    """
    # copy value
    try:
        value = value.copy()
    except AttributeError:
        pass

    # parse data
    if ":" in key:
        value = str(value)
        netcdf_dtype = "attribute"
    elif "S" in dimensions:
        value = np.array(value, dtype="S" + str(S))
        value = _nd_array(value, len(dimensions))
        netcdf_dtype = 'S1'
    elif "S" not in dimensions:
        value = _nd_array(value, len(dimensions))
        netcdf_dtype = "f8"
    else:
        raise ValueError((
            f"Something went wrong in sofa['{key}']. This is either a bug or "
            "an error in the convention. 'value' is an attribute if the key "
            "contains ':'. In this case the input value must be convertible "
            "to a string. 'value' is a string variable if the dimensions "
            "contain 'S'. In this case the input value must be a string, a "
            "list of strings or a numpy fixed length byte array, e.g., "
            "np.array(data, dtype='S10'). 'vale is a float variable if "
            "dimensions does not contain 'S'. In this case it must be "
            "convertible to a numpy array."))

    return value, netcdf_dtype


def _format_value_from_netcdf(value, key):
    """
    Format value from NETCDF4 file for saving in a SOFA dictionairy

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

    if str(value.dtype).startswith("float"):
        if np.ma.is_masked(value):
            warnings.warn(f"Entry {key} contains missing data")
        else:
            # Convert to numpy array or scalar
            value = np.asarray(value)
    elif str(value.dtype).startswith("|S"):
        # string arrays are stored in masked arrays with empty strings '' being
        # masked. Convert to regular arrays with unmasked empty strings
        value = np.asarray(value)
        # decode binary format
        value = value.astype("U")
    else:
        raise TypeError(
            f"{key}: value.dtype is {value.dtype} but must be float or S")

    # convert arrays to scalars if they do not store data that is usually used
    # as scalar metadata, e.g., the SamplingRate
    data_keys = ["Data.IR", "Data.Real", "Data.Imag", "Data.SOS" "Data.Delay"]
    if value.size == 1 and key not in data_keys:
        value = value[0]

    return value


def _is_mandatory(flags):
    """
    Check if a field is mandatory

    Parameters
    ----------
    flags : None, str
        The flags from convention[key]["flags"]

    Returns
    -------
    is_mandatory : bool
    """
    # skip optional fields if requested
    if flags is None:
        is_mandatory = False
    elif "m" not in flags:
        is_mandatory = False
    else:
        is_mandatory = True

    return is_mandatory


def _get_size_and_shape_of_string_var(value, key):
    """
    String variables can be strings, list of strings, or numpy arrays of
    strings. This functions returns the length of the longest string S inside
    the string variable and the shape of the string variable as required by
    the SOFA definition. Note that the shape is the shape of the array that
    holds the strings. NETCDF stores all string variables in arrays.
    """

    if isinstance(value, str):
        S = len(value)
        shape = (1, 1)
    elif isinstance(value, list):
        S = len(max(value, key=len))
        shape = np.array(value).shape
    elif isinstance(value, np.ndarray):
        S = max(np.vectorize(len)(value))
        shape = value.shape
    else:
        raise ValueError(
            (f"sofa['{key}'] must be a string, numpy string "
                "array, or list of strings"))

    return S, shape


def _nd_array(array, ndim):
    """
    Get numpy array with specified number of dimensions. Dimensions are
    appended at the end if the input array has less dimensions.
    """
    try:
        array = array.copy()
    except AttributeError:
        array = array

    if ndim == 1:
        array = np.atleast_1d(array)
    if ndim == 2:
        array = np.atleast_2d(array)
    if ndim >= 3:
        array = np.atleast_3d(array)
    for _ in range(ndim - array.ndim):
        array = array[..., np.newaxis]
    return array
