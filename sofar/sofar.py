import os
import glob
import json
import requests
from functools import reduce
import operator
from datetime import datetime
import platform
from packaging import version
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


def list_conventions(print_conventions=True, return_paths=False):
    """
    List available SOFA conventions.

    Parameters
    ----------
    print_conventions : bool, optional
        Print the names and versions of the currently supported conventions to
        the console. The default is ``True``.
    return_paths : bool, optional
        Return a list containing the full paths of the files that store the
        conventions. The default is ``False``.

    Returns
    -------
    paths : list
        The full paths of the SOFA convention files. A SOFA convention defines
        the kind of data and the data format that is stored in a SOFA file.
        The paths are only returned if `return_paths` is ``True`` (see
        Parameters).

    Notes
    -----
    For updating the local convention files see
    :py:func:`~sofar.update_conventions`.
    """
    # directory containing the SOFA conventions
    directory = os.path.join(os.path.dirname(__file__), "conventions")

    # SOFA convention files
    paths = [file for file in glob.glob(os.path.join(directory, "*.json"))]

    if print_conventions:
        print("Available SOFA conventions:")
        for path in paths:
            fileparts = os.path.basename(path).split(sep="_")
            convention = fileparts[0]
            version_str = fileparts[1][:-5]
            print(f"{convention} (Version {version_str})")

    if return_paths:
        return paths


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
    is because Python dictionaries are mutable objects.
    """

    if not isinstance(key, list):
        key = [key]

    # check if the key is valid
    # (this raises an error if the key does not exist)
    current_value = _get_from_nested_dict(sofa, key)
    # (this raises an error if the key does not belong to a value)
    if isinstance(current_value, dict):
        raise ValueError(
            f"The attribute {key} is not contained in the convention")

    # set the value
    _set_in_nested_dict(sofa, key, value)


def write_sofa(filename: str, sofa: dict):

    # check the filename
    if not filename.lower().endswith('.sofa'):
        filename += ".sofa"

    # open new NETCDF4 file for writing
    with Dataset(filename, "w", format="NETCDF4") as file:

        # write dimensions
        for dim in sofa["API"]:
            # Dimensions are stored in single upper case letters - skip others
            if len(dim) > 1 or dim.islower():
                continue
            # create the dimension
            file.createDimension(dim, sofa["API"][dim])


def _convention_csv2dict(file: str):
    """
    Read SOFA convention from csv file. The csv files are taken from the
    official Matlab/Octave SOFA API.

    Parameters
    ----------
    file : str
        filename of the SOFA convention

    Returns
    -------
    convention : dict
        SOFA convention as dictionary. Each key has a list of four entries
        entries that are according to `convention['comment']`.

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

            # write first line (as kind of comment)
            if idl == 0:
                fields = line[1:]
                continue

            # add blank comment if it does not exist
            if len(line) == 5:
                line.append("")

            # write second to last line
            convention[line[0]] = {}
            for ff, field in enumerate(fields):
                convention[line[0]][field.lower()] = line[ff + 1]

        except: # noqa
            raise ValueError((f"Failed to parse line {idl}, entry {idc} in: "
                              f"{file}: \n{line}\n"))

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
    paths = list_conventions(False, True)
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
    Convert a SOFA convention to an SOFA file with default values

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
    sofa["Data"] = {}

    # populate the SOFA file
    for key in convention.keys():

        # comment field is not part of the convention
        if key == "comment":
            continue

        # skip optional fields if requested
        if not _is_mandatory(convention, key) and mandatory:
            continue

        # get default value and key as list of key(s)
        value, keys = _get_default_and_keylist(convention, key)
        _set_in_nested_dict(sofa, keys, value)

    # move entries Data and API to the end
    sofa["Data"] = sofa.pop("Data")

    # write API and date specific read only fields
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sofa["GLOBAL:DateCreated"] = now
    sofa["GLOBAL:DateModified"] = now
    sofa["GLOBAL:APIName"] = "sofar SOFA API for Python (pyfar.org)"
    sofa["GLOBAL:APIVersion"] = sf.__version__
    sofa["GLOBAL:ApplicationName"] = "Python"
    sofa["GLOBAL:ApplicationVersion"] = platform.python_version()

    # add the API
    sofa = _add_api(convention, sofa, mandatory)

    return sofa


def _add_api(convention, sofa, mandatory):
    """
    Add API to an empty SOFA file

    Parameters
    ----------
    convention : dict
        The SOFA convention
    sofa : dict
        The empty SOFA file without API
    mandatory : bool
        Flag to indicate if only mandatory fields are included in the SOFA file

    Returns
    -------
    sofa : dict
        The SOFA file with default values
    """

    # initialize SOFA API
    sofa["API"] = {}
    sofa["API"]["Dimensions"] = {}
    sofa["API"]["Dimensions"]["Data"] = {}

    # populate the SOFA file
    for key in convention.keys():

        # comment field is not part of the convention
        if key == "comment":
            continue

        # skip optional fields if requested
        if not _is_mandatory(convention, key) and mandatory:
            continue

        # get default value and key as list of key(s)
        value, keys = _get_default_and_keylist(convention, key)

        # update API
        dimensions = convention[key][2]
        if dimensions is not None:
            # add dimensions to API
            dimensions = dimensions.split(", ") if "," in dimensions \
                else [dimensions]
            _set_in_nested_dict(
                sofa, ["API", "Dimensions"] + keys, dimensions)

            # add size of dimension and the field determing the size
            for id, dim in enumerate(dimensions[0]):
                if dim.islower():
                    sofa["API"][dim.upper()] = \
                        _atleast_4d(value).shape[id]
                    sofa["API"][dim] = keys

    # add fixed sizes
    sofa["API"]["C"] = 3
    sofa["API"]["I"] = 1

    return sofa


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
    if convention[key][1] is None:
        is_mandatory = False
    elif "m" not in convention[key][1]:
        is_mandatory = False
    else:
        is_mandatory = True

    return is_mandatory


def _get_default_and_keylist(convention: dict, key: str):
    """
    1. Return default value from convention based on key.
    2. Convert key to list of (nested) keys.
    """
    # replacing to be comparable to the Matlab/Octave API)
    keys = key.replace(":", ":")
    # split key for accessing nested dictionary
    keys = keys.split(".") if "." in keys else [keys]

    # get the default value
    value = convention[key][0]
    value = "" if value is None else value

    return value, keys


def _update_dimensions(sofa):
    pass


def _get_from_nested_dict(dictionary, keys):
    "Get value from nested dictionary based on a list of keys."
    try:
        value = reduce(operator.getitem, keys, dictionary)
    except KeyError:
        raise ValueError(
            f"The attribute {keys} is not contained in the convention")

    return value


def _set_in_nested_dict(dictionary, keys, value):
    "Set value in nested dictionary based on a list of keys."
    _get_from_nested_dict(dictionary, keys[:-1])[keys[-1]] = value


def _atleast_4d(value):
    """
    Return value as numpy array with ndims=4, which is the maximum number of
    dimensions an array stored in a SOFA file can have.
    """
    value = np.atleast_3d(value)
    if value.ndim == 3:
        value = np.atleast_3d(value)[..., np.newaxis]
    return value
