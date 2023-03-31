import os
import glob
import numpy as np
import numpy.testing as npt
import warnings
import sofar as sf


def version():
    """Return version of sofar and SOFA conventions"""

    sofa_conventions = os.path.join(
        os.path.dirname(__file__), "sofa_conventions", 'VERSION')
    with open(sofa_conventions) as file:
        sofa_conventions = file.readline().strip()

    return (f"sofar v{sf.__version__} implementing "
            f"SOFA standard {sofa_conventions}")


def _verify_convention_and_version(version, convention):
    """
    Verify if convention and version exist. Raise a Value error if it does not.

    Parameters
    ----------
    version : str
        The version to be checked
    convention : str
        The name of the convention to be checked
    """

    # check if the convention exists
    if convention not in _get_conventions("name"):
        raise ValueError(
            f"Convention '{convention}' does not exist")

    name_version = _get_conventions("name_version")

    # check which version is wanted
    version_exists = False
    for versions in name_version:
        # check if convention and version match
        if versions[0] == convention \
                and str(float(versions[1])) == version:
            version_exists = True

    if not version_exists:
        raise ValueError((
            f"{convention} v{version} is not a valid SOFA Convention."
            "If you are trying to read the data use "
            "sofar.read_sofa_as_netcdf(). Call sofar.list_conventions() for a "
            "list of valid Conventions"))


def list_conventions():
    """
    List available SOFA conventions by printing to the console.
    """
    print(_get_conventions("string"))


def _get_conventions(return_type, conventions_path=None):
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
    conventions_path : str, optional
        The path to the the `conventions` folder containing the csv and json
        files.

    Returns
    -------
    See parameter `return_type`.
    """
    # directory containing the SOFA conventions
    if conventions_path is None:
        conventions_path = os.path.join(
            os.path.dirname(__file__), "sofa_conventions", 'conventions')

    reg_str = "*.csv" if return_type == "path_source" else "*.json"

    # SOFA convention files
    standardized = list(glob.glob(os.path.join(conventions_path, reg_str)))
    deprecated = list(
        glob.glob(os.path.join(conventions_path, "deprecated", reg_str)))
    paths = standardized + deprecated

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
        return list(zip(conventions, versions))
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
        return _equals_raise_warning((
            f"not identical: sofa_a has {len(keys_a)} attributes for "
            f"comparison and sofa_b has {len(keys_b)}."), verbose)

    # check if the keys match
    if set(keys_a) != set(keys_b):
        return _equals_raise_warning(
            "not identical: sofa_a and sofa_b do not have the ame attributes",
            verbose)

    # compare the data inside the SOFA object
    for key in keys_a:

        # get data and types
        a = getattr(sofa_a, key)
        b = getattr(sofa_b, key)
        type_a = sofa_a._convention[key]["type"]
        type_b = sofa_b._convention[key]["type"]

        # compare attributes
        if type_a == "attribute" and type_b == "attribute":

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
    sofa.add_attribute("GLOBAL_EmitterDescription", "what an emitter")
    sofa.add_variable("EmitterDescriptions", ["emitter array"], "string", "MS")
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
