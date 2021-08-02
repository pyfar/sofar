import os
import glob
import json
import requests
from functools import reduce
import operator
import numpy as np
from bs4 import BeautifulSoup


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

        # convert SOFA conventions definition from csv to json
        convention_dict = _definition_csv2dict(filename_csv)

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
            version = fileparts[1][:-5]
            print(f"{convention} (Version {version})")

    if return_paths:
        return paths


def get_convention(name, mandatory=True):
    """Get definition of SOFA convention from json file.

    Parameters
    ----------
    name : str
        The name of the convention. See :py:func:`~sofar.list_conventions`.

    Returns
    -------
    definition : dict
        The definition of the SOFA convention as dictionary. The definition is
        read from the corresponding json file. See
        :py:func:`~sofar.list_conventions`.
    """

    # check input
    if not isinstance(name, str):
        raise TypeError(
            f"Convention must be a string but is of type {type(name)}")

    # load convention definition from json file
    paths = list_conventions(False, True)
    path = [path for path in paths if name in path]

    if not len(path):
        raise ValueError(
            (f"Convention '{name}' not found. See "
             "sofar.list_conventions() for available conventions."))
    if len(path) > 1:
        raise ValueError(
            (f"Found multiple matches for convention '{name}'. See "
             "sofar.list_conventions() for available conventions."))

    with open(path[0], "r") as file:
        definition = json.load(file)

    # convert convention definition to SOFA file in dict format
    convention = _definition2convention(definition)

    return convention


def _definition_csv2dict(file: str):
    """
    Read SOFA convention definition from csv file. The csv files are taken
    from the official Matlab/Octave SOFA API.

    Parameters
    ----------
    file : str
        filename of the SOFA convention definition

    Returns
    -------
    convention : dict
        SOFA convention definition as dictionary. Each key has a list of four
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
                convention["comment"] = line[1:]
                continue

            # write second to last line
            convention[line[0]] = line[1:]
        except: # noqa
            raise ValueError((f"Failed to parse line {idl}, entry {idc} in: "
                              f"{file}: \n{line}\n"))

    return convention


def _definition2convention(definition):

    # initialize convention
    convention = {}

    # populate the convention
    for key in definition.keys():

        # comment field is not part of the definition
        if key == "comment":
            continue

        # replacing to be comparable to the Matlab/Octave API)
        keys = key.replace(":", "_")
        # split key for accessing nested dictionary
        keys = keys.split(".") if "." in keys else [keys]

        # set default value
        value = definition[key][0]
        value = "" if value is None else value
        _set_in_nested_dict(convention, keys, value)

        # update API
        dimensions = definition[key][2]
        if dimensions is not None:
            # add dimensions to API
            dimensions = dimensions.split(", ") if "," in dimensions \
                else [dimensions]
            _set_in_nested_dict(
                convention, ["API", "Dimensions"] + keys, dimensions)

            # add size of dimension
            for dimension in dimensions:
                for id, dim in enumerate(dimension):
                    if dim.islower():
                        _set_in_nested_dict(
                            convention,
                            ["API", dim.upper()],
                            _atleast_4d(value).shape[id])

    # add fixed sizes
    convention["API"]["C"] = 3
    convention["API"]["I"] = 1

    # move entries Data and API to the end
    convention["Data"] = convention.pop("Data")
    convention["API"] = convention.pop("API")

    # TODO:
    # add GLOBAL_DateCreated/APIVersion/APIName'
    # remove non mandatory fields if requested
    # modularize get_convention

    return convention


def _get_from_nested_dict(dictionary, keys):
    "Get value from nested dictionary based on a list of keys."
    return reduce(operator.getitem, keys, dictionary)


def _set_in_nested_dict(dictionary, keys, value):
    "Set value in nested dictionary based on a list of keys."
    _get_from_nested_dict(dictionary, keys[:-1])[keys[-1]] = value


def _atleast_4d(value):
    """return value as numpy array with four dimensions"""
    value = np.atleast_3d(value)
    if value.ndim == 3:
        value = np.atleast_3d(value)[..., np.newaxis]
    return value
