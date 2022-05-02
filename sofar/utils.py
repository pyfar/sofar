import os
import glob
import json
import requests
import numpy as np
import numpy.testing as npt
from packaging.version import parse as version_parse
import warnings
from bs4 import BeautifulSoup
import sofar as sf


def update_conventions(conventions_path=None, assume_yes=False):
    """
    Update SOFA conventions.

    SOFA convention define what data is stored in a SOFA file and how it is
    stored. Updating makes sure that sofar is using the latest conventions.
    This is done in three steps

    1.
        Download official SOFA conventions as csv files from
        https://github.com/sofacoustics/API_MO/tree/master/API_MO/conventions.
    2.
        Convert csv files to json files to be read by sofar.
    3.
        Notify which conventions were newly added or updated.

    The csv and json files are stored at sofar/conventions. Sofar works only on
    the json files. To get a list of all currently available SOFA conventions
    and their paths see :py:func:`~sofar.list_conventions`.

    .. note::
        If the official convention contain errors, calling this function might
        break sofar. If this is the case sofar must be re-installed, e.g., by
        running ``pip install --force-reinstall sofar``. Be sure that you want
        to do this.

    Parameters
    ----------
    conventions_path : str, optional
        Path to the folder where the conventions are saved. The default is
        ``None``, which saves the conventions inside the sofar package.
        Conventions saved under a different path can not be used by sofar. This
        parameter was added mostly for testing and debugging.
    response : bool, optional

        ``True``
            Updating the conventions must be confirmed by typing "y".
        ``False``
            The conventions are updated without confirmation.

        The default is ``True``
    """

    if not assume_yes:
        # these lines were only tested manually. I was too lazy to write a test
        # coping with keyboard input
        print(("Are you sure that you want to update the conventions? "
               "Read the documentation before continuing. "
               "If updateing breaks sofar it has to be re-installed"
               "(y/n)"))
        response = input()
        if response != "y":
            print("Updating the conventions was canceled.")
            return

    # url for parsing and downloading the convention files
    url = ("https://github.com/sofacoustics/API_MO/tree/"
           "master/API_MO/conventions")
    url_raw = ("https://raw.githubusercontent.com/sofacoustics/API_MO/"
               "master/API_MO/conventions")
    ext = 'csv'

    print(f"Reading SOFA conventions from {url} ...")

    # get file names of conventions from the SOFA Matlab/Octave API
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    conventions = [os.path.split(node.get('href'))[1]
                   for node in soup.find_all('a')
                   if node.get('href').endswith(ext)]

    # directory handling
    if conventions_path is None:
        conventions_path = os.path.join(os.path.dirname(__file__),
                                        "conventions")
    if not os.path.isdir(os.path.join(conventions_path, "source")):
        os.mkdir(os.path.join(conventions_path, "source"))

    # Loop and download conventions if they changed
    updated = False
    for convention in conventions:

        # exclude these conventions
        if convention.startswith(("General_", "GeneralString_")):
            continue

        filename_csv = os.path.join(conventions_path, "source", convention)

        # download SOFA convention definitions to package diretory
        data = requests.get(url_raw + "/" + convention)
        # remove trailing tabs
        data = data.content.replace(b"\t\n", b"\n").replace(b"\r\n", b"\n")

        # check if convention needs to be added or updated
        update = False
        if not os.path.isfile(filename_csv):
            update = True
            updated = f"- added new convention: {convention}"
        else:
            with open(filename_csv, "rb") as file:
                data_current = b"".join(file.readlines())
                data_current = data_current.replace(b"\r\n", b"\n")
            if data_current != data:
                update = True
                updated = f"- updated existing convention: {convention}"

        # update convention
        if update:
            with open(filename_csv, "wb") as file:
                file.write(data)
            print(updated)

    # compile json files from csv file
    # (this is also done if nothing changed. It won't affect the content of
    #  the json files but the time-stamp will be updated)
    _compile_conventions()

    if updated:
        print("... done.")
    else:
        print("... conventions already up to date.")


def _compile_conventions(conventions_path=None):
    """
    Compile SOFA conventions (json files) from source conventions (csv files
    from SOFA API_MO), i.e., only do step 2 from `update_conventions`. This is
    a helper function for debugging and developing and might break sofar.

    Parameters
    ----------
    conventions_path : str
        Path to the folder containing the conventions as json files (might be
        empty) and the source convention as csv files in the subfolder `source`
        (must not be empty). The default is ``None``, which uses the
        default location inside the sofar package.
    """
    # directory handling
    if conventions_path is None:
        conventions_path = os.path.join(os.path.dirname(__file__),
                                        "conventions")
    if not os.path.isdir(os.path.join(conventions_path, "source")):
        raise ValueError("conventions_path must contain the folder 'source'")

    # get list of source conventions
    csv_files = glob.glob(os.path.join(
        conventions_path, "source", "*.csv"))
    csv_files = [os.path.split(csv_file)[1] for csv_file in csv_files]

    for csv_file in csv_files:

        # directories for reading and writing
        json_file = os.path.join(conventions_path, csv_file[:-3] + "json")
        csv_file = os.path.join(conventions_path, "source", csv_file)

        # convert SOFA conventions from csv to json
        convention_dict = _convention_csv2dict(csv_file)
        with open(json_file, 'w') as file:
            json.dump(convention_dict, file, indent=4)


def _verify_convention_and_version(version, version_in, convention):
    """
    Verify if convention and version exist and return version

    Parameters
    ----------
    version : str
        'latest', 'match', version string (e.g., '1.0')
    version_in : str
        The version to be checked against
    convention : str
        The name of the convention to be checked

    Returns
    -------
    version_out : str
        The version to be used depending on `version`, and `version_in`
    """

    # check if the convention exists in sofar
    if convention not in _get_conventions("name"):
        raise ValueError(
            f"Convention '{convention}' does not exist")

    name_version = _get_conventions("name_version")

    if version == "latest":
        # get list of versions as floats
        version_out = [float(versions[1]) for versions in name_version
                       if versions[0] == convention]
        # get latest version as string
        version_out = str(version_out[np.argmax(version_out)])

        if version_parse(version_out) > version_parse(version_in):
            print(("Updated conventions version from "
                   f"{version_in} to {version_out}"))
    else:
        # check which version is wanted
        if version == "match":
            match = version_in
        else:
            match = version

        version_out = None
        for versions in name_version:
            # check if convention and version match
            if versions[0] == convention \
                    and str(float(versions[1])) == match:
                version_out = str(float(versions[1]))

        if version_out is None:
            raise ValueError((
                f"Version {match} does not exist for convention {convention}. "
                "Try to access the data with version='latest'"))

    return version_out


def list_conventions():
    """
    List available SOFA conventions by printing to the console.
    """
    print(_get_conventions("string"))


def _get_conventions(return_type):
    """
    Get available SOFA conventions.

    Parameters
    ----------
    return_type : string, optional
        ``'path'``
            Return a list with the full paths and filenames of the convention
            files (json files)
        ``'path_source'``
            Return a list with the full paths and filenames of the source
            convention files from API_MO (csv files)
        ``'name'``
            Return a list of the convention names without version
        ``'name_version'``
            Return a list of tuples containing the convention name and version.
        ``'string'``
            Returns a string that lists the names and versions of all
            conventions.

    Returns
    -------
    See parameter `return_type`.
    """
    # directory containing the SOFA conventions
    if return_type == "path_source":
        directory = os.path.join(
            os.path.dirname(__file__), "conventions", "source")
        reg_str = "*.csv"
    else:
        directory = os.path.join(os.path.dirname(__file__), "conventions")
        reg_str = "*.json"

    # SOFA convention files
    paths = [file for file in glob.glob(os.path.join(directory, reg_str))]

    conventions_str = "Available SOFA conventions:\n"

    conventions = []
    versions = []
    for path in paths:
        fileparts = os.path.basename(path).split(sep="_")
        conventions += [fileparts[0]]
        versions += [fileparts[1][:-5]]
        conventions_str += f"{conventions[-1]} (Version {versions[-1]})\n"

    if return_type is None:
        return
    elif return_type.startswith("path"):
        return paths
    elif return_type == "name":
        return conventions
    elif return_type == "name_version":
        return [(n, v) for n, v in zip(conventions, versions)]
    elif return_type == "string":
        return conventions_str
    else:
        raise ValueError(f"return_type {return_type} is invalid")


def equals(sofa_a, sofa_b, verbose=True, exclude=None):
    """
    Compare two SOFA objects against each other.

    Parameters
    ----------
    sofa_a : Sofa
        SOFA object
    sofa_b : Sofa
        SOFA object
    verbose : bool, optional
        Print differences to the console. The default is True.
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
        ``True`` if sofa_a and sofa_b are identical, ``False`` otherwise.
    """

    is_identical = True

    # get and filter keys
    # ('_*' are SOFA object private variables, '__' are netCDF attributes)
    keys_a = [k for k in sofa_a.__dict__.keys() if not k.startswith("_")]
    keys_b = [k for k in sofa_b.__dict__.keys() if not k.startswith("_")]

    if exclude is not None:
        if exclude.upper() == "GLOBAL":
            keys_a = [k for k in keys_a if not k.startswith("GLOBAL_")]
            keys_b = [k for k in keys_b if not k.startswith("GLOBAL_")]
        elif exclude.upper() == "ATTR":
            keys_a = [k for k in keys_a if
                      sofa_a._convention[k]["type"] != "attribute"]
            keys_b = [k for k in keys_b if
                      sofa_b._convention[k]["type"] != "attribute"]
        elif exclude.upper() == "DATE":
            keys_a = [k for k in keys_a if "Date" not in k]
            keys_b = [k for k in keys_b if "Date" not in k]
        else:
            raise ValueError(
                f"exclude is {exclude} but must be GLOBAL, DATE, or ATTR")

    # check for equal length
    if len(keys_a) != len(keys_b):
        is_identical = _equals_raise_warning((
            f"not identical: sofa_a has {len(keys_a)} attributes for "
            f"comparison and sofa_b has {len(keys_b)}."), verbose)

        return is_identical

    # check if the keys match
    if set(keys_a) != set(keys_b):
        is_identical = _equals_raise_warning(
            "not identical: sofa_a and sofa_b do not have the ame attributes",
            verbose)

        return is_identical

    # compare the data inside the SOFA object
    for key in keys_a:

        # get data and types
        a = getattr(sofa_a, key)
        b = getattr(sofa_b, key)
        type_a = sofa_a._convention[key]["type"]
        type_b = sofa_b._convention[key]["type"]

        # compare attributes
        if type_a == "attribute" and type_b == "attribute":

            # handling versions (might be integer, float, or string)
            if not isinstance(a, str) or not isinstance(a, str):
                a = str(float(a))
                b = str(float(b))

            # compare
            if a != b:
                is_identical = _equals_raise_warning(
                    f"not identical: different values for {key}", verbose)

        # compare double variables
        elif type_a == "double" and type_b == "double":

            try:
                npt.assert_allclose(np.squeeze(a), np.squeeze(b))
            except AssertionError:
                is_identical = _equals_raise_warning(
                    "not identical: different values for {key}", verbose)

        # compare string variables
        elif type_a == "string" and type_b == "string":
            try:
                assert np.all(
                    np.squeeze(a).astype("S") == np.squeeze(b).astype("S"))
            except AssertionError:
                is_identical = _equals_raise_warning(
                    "not identical: different values for {key}", verbose)
        else:
            is_identical = _equals_raise_warning(
                (f"not identical: {key} has different data types "
                 f"({type_a}, {type_b})"), verbose)

    return is_identical


def _equals_raise_warning(message, verbose):
    if verbose:
        warnings.warn(message)
    return False


def _convention_csv2dict(file: str):
    """
    Read a SOFA convention as csv file from the official Matlab/Octave API for
    SOFA (API_MO) and convert them to a Python dictionary. The dictionary can
    be written for example to a json file using

    import json

    with open(filename, 'w') as file:
        json.dump(dictionary, file, indent=4)

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
    # (encoding should be changed to utf-8 after the SOFA conventions repo is
    # clean.)
    # TODO: add explicit test for this function that checks the output
    with open(file, 'r', encoding="windows-1252") as fid:
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
            # convert versions to strings
            if "Version" in line[0] and not isinstance(line[1], str):
                line[1] = str(float(line[1]))

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


def _atleast_nd(array, ndim):
    """
    Get numpy array with specified number of dimensions. Dimensions are
    appended at the end if ndim > 3.
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


def _nd_newaxis(array, ndim):
    """Append dimensions to the end of an array until array.ndim == ndim"""
    array = np.array(array)

    for _ in range(ndim - array.ndim):
        array = array[..., np.newaxis]
    return array


def _complete_sofa(convention="GeneralTF"):
    """
    Generate SOFA file with all required data for testing verification rules.
    """

    sofa = sf.Sofa(convention)
    # Listener meta data
    sofa.add_variable("ListenerView", [1, 0, 0], "double", "IC")
    sofa.add_attribute("ListenerView_Type", "cartesian")
    sofa.add_attribute("ListenerView_Units", "metre")
    sofa.add_variable("ListenerUp", [0, 0, 1], "double", "IC")
    # Receiver meta data
    sofa.add_variable("ReceiverView", [1, 0, 0], "double", "IC")
    sofa.add_attribute("ReceiverView_Type", "cartesian")
    sofa.add_attribute("ReceiverView_Units", "metre")
    sofa.add_variable("ReceiverUp", [0, 0, 1], "double", "IC")
    # Source meta data
    sofa.add_variable("SourceView", [1, 0, 0], "double", "IC")
    sofa.add_attribute("SourceView_Type", "cartesian")
    sofa.add_attribute("SourceView_Units", "metre")
    sofa.add_variable("SourceUp", [0, 0, 1], "double", "IC")
    # Emitter meta data
    sofa.add_variable("EmitterView", [1, 0, 0], "double", "IC")
    sofa.add_attribute("EmitterView_Type", "cartesian")
    sofa.add_attribute("EmitterView_Units", "metre")
    sofa.add_variable("EmitterUp", [0, 0, 1], "double", "IC")
    # Room meta data
    sofa.add_attribute("GLOBAL_RoomShortName", "Hall")
    sofa.add_attribute("GLOBAL_RoomDescription", "Wooden floor")
    sofa.add_attribute("GLOBAL_RoomLocation", "some where nice")
    sofa.add_variable("RoomTemperature", 0, "double", "I")
    sofa.add_attribute("RoomTemperature_Units", "kelvin")
    sofa.add_attribute("GLOBAL_RoomGeometry", "some/file")
    sofa.add_variable("RoomVolume", 200, "double", "I")
    sofa.add_attribute("RoomVolume_Units", "cubic metre")
    sofa.add_variable("RoomCornerA", [0, 0, 0], "double", "IC")
    sofa.add_variable("RoomCornerB", [1, 1, 1], "double", "IC")
    sofa.add_variable("RoomCorners", 0, "double", "I")
    sofa.add_attribute("RoomCorners_Type", "cartesian")
    sofa.add_attribute("RoomCorners_Units", "metre")

    sofa.verify()
    return sofa
