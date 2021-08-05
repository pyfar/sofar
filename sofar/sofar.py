import os
import glob
import json
import requests
from datetime import datetime
import platform
import numpy as np
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


def create_sofa(convention, mandatory=False):
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

    Returns
    -------
    convention : dict
        The SOFA convention with the default values as dictionary.
    """

    # get convention
    convention = _load_convention(convention)
    # convert convention to SOFA file in dict format
    sofa = _convention2sofa(convention, mandatory)
    # add and update the API
    _add_api(sofa, convention)
    update_api(sofa)

    return sofa


def set_value(sofa, key, value):
    """
    Set value specified by the key in a SOFA file.

    Parameters
    ----------
    sofa : dict
        A SOFA file obtained from :py:func:`~sofar.create_sofa`.
    key : str, list of strings
        The name of the attribute to which the value is assigned, i.e.,
        ``'ListenerPosition'``, or ``['Data', 'IR']``.
    value : number, string, list, array
        The value to be assigned.

    Retruns
    -------
    The value is updated in `sofa` without the need for returning it. This
    is because Python dictionaries are mutable objects. Lists are converted
    to numpy arrays.
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


def update_api(sofa):

    sofa["API"]["Dimensions"] = {}

    # get all keys except API
    keys = [key for key in sofa.keys() if key != "API"]

    # first run: Get the dimensions for E, R, M, N, and S
    S = 0
    for key in keys:

        value = sofa[key]
        dimensions = sofa["API"]["Convention"][key]["dimensions"]

        if dimensions is None:
            continue

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

    # second run: verify dimensions of data
    for key in keys:

        # handle dimensions
        dimensions = sofa["API"]["Convention"][key]["dimensions"]

        if dimensions is None:
            continue

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

            shape_ref = tuple([sofa["API"][d.upper()] for d in dim])
            shape_compare = shape_act[:len(shape_ref)]

            if "S" in dimensions:
                # the last dimension is S which can be smaller
                # (e.g. if S=12, there can still be shorter strings in the
                #  dict. The length is corrected during writing to disk)
                if shape_compare[:-1] == shape_ref[:-1] \
                        and shape_compare[-1] <= shape_ref[-1]:
                    shape_matched = True
            else:
                # check if the entire shapes match
                if shape_compare == shape_ref:
                    shape_matched = True

            if shape_matched:
                sofa["API"]["Dimensions"][key] = dim.upper()
                break

        if not shape_matched:
            raise ValueError(
                (f"The shape of {key} is {shape_compare} but has "
                 f"to be: {dimensions.upper()} "
                 "(see field 'API' in the SOFA file)"))


def write_sofa(filename: str, sofa: dict):

    # check the filename
    if not filename.lower().endswith('.sofa'):
        filename += ".sofa"

    # update the dimensions
    update_api(sofa)

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
            tmp_var[:] = value

            # write variable attributes
            sub_keys = [k for k in sofa.keys() if k.startswith(key + ":")]
            for sub_key in sub_keys:
                setattr(tmp_var, sub_key[len(key)+1:], str(sofa[sub_key]))


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


def _load_convention(convention):
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

    # load convention from json file
    paths = list_conventions(False, "path")
    path = [path for path in paths
            if os.path.basename(path).startswith(convention + "_")]

    if not len(path):
        raise ValueError(
            (f"Convention '{convention}' not found. See "
             "sofar.list_conventions() for available conventions."))

    with open(path[0], "r") as file:
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
        if not _is_mandatory(convention, key) and mandatory:
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


def _add_api(sofa, convention=None):
    """
    Add API to SOFA file. If The SOFA files contains an API it is overwritten.

    The API is basically the convention file, which holds the meta data that is
    required for writing the SOFA file to disk.

    Parameters
    ----------
    sofa : dict
        The SOFA file without API
    convention : dict, optional
        The SOFA convention as a dict. If no dict is provided, the convention
        is read from the SOFA file and loaded accordingly.

    Returns
    -------
    sofa : dict
        The SOFA file with API
    """

    # load the convention if required
    if convention is None:
        convention = _load_convention(sofa["GLOBAL:SOFAConventions"])

    # initialize SOFA API
    keys = [key for key in sofa.keys()]
    sofa["API"] = {}
    sofa["API"]["Convention"] = {}

    # populate the SOFA API
    for key in keys:
        sofa["API"]["Convention"][key] = convention[key]


def _format_value_for_netcdf(value, key, dimensions, S):

    # copy value
    try:
        value = value.copy()
    except AttributeError:
        value = value

    # parse data
    if ":" in key:
        value = str(value)
        netcdf_dtype = "attribute"
    elif "S" in dimensions:
        value = np.array(value, dtype="S" + str(S))
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


def _is_mandatory(convention, key):
    """
    Check if a field is mandatory

    Parameters
    ----------
    convention : dict
        The SOFA convention
    key : string
        The field to be checked

    Returns
    -------
    is_mandatory : bool
    """
    # skip optional fields if requested
    if convention[key]["flags"] is None:
        is_mandatory = False
    elif "m" not in convention[key]["flags"]:
        is_mandatory = False
    else:
        is_mandatory = True

    return is_mandatory


def _get_size_and_shape_of_string_var(value, key):
    """
    String variables can be strings, list of strings, or numpy arrays of
    strings. This functions returns the length of the longest string S inside
    the string variable and the shape of the string variable as required by
    the SOFA definition.
    """

    if isinstance(value, str):
        S = len(value)
        shape = (1, S)
    elif isinstance(value, list):
        S = len(max(value, key=len))
        shape = (len(value), S)
    elif isinstance(value, np.ndarray):
        S = max(np.vectorize(len)(value))
        shape = value.shape + (S, )
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
    if ndim == 1:
        array = np.atleast_1d(array)
    if ndim == 2:
        array = np.atleast_2d(array)
    if ndim >= 3:
        array = np.atleast_3d(array)
    for _ in range(ndim - array.ndim):
        array = array[..., np.newaxis]
    return array
