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


class Sofa():
    """Create a SOFA file with default values.

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
        default is ``'latest'``. Also see
        :py:func:`~sofar.list_conventions`.
    update_api : bool, optional
        Update the API by calling :py:func:`~Sofa.update_api`. This helps
        to find potential errors in the default values and is thus recommended.
        If reading a file does not work, try to call `Sofa` with
        ``update=False``. The default is ``True``.

    Returns
    -------
    sofa : Sofa
        A SOFA object filled with the default values of the convention.

    Examples
    --------
    .. code-block:: python

        import sofar as sf

        # create SOFA object
        sofa = sf.Sofa("SimpleFreeFieldHRIR")

    For more examples refer to the documentation at
    https://pyfar.readthedocs.io/en/latest/
    """

    # these have to be set here, because they are used in __setattr__ and
    # Python checks if they exist upon class creation
    _frozen = False  # do not allow to add attributes if True
    _read_only = []  # list of read only attributes

    def __init__(self, convention, mandatory=False, version="latest",
                 update_api=True):
        """See class docstring"""

        # get convention
        self._convention = self._load_convention(convention, version)

        # update read only attributes
        self._read_only = [
            key for key in self._convention.keys()
            if _is_read_only(self._convention[key]["flags"])]

        # add attributes with default values
        self._convention2sofa(mandatory)

        # add and update the API
        # TODO class style
        if update_api:
            self.update_api(version)

        self._frozen = True

    def __setattr__(self, name: str, value):
        # don't allow new attributes to be added outside the class
        if self._frozen and not hasattr(self, name):
            raise TypeError(f"{name} is an invalid attribute")
        # don't allow setting read only attributes
        if name in self._read_only and self._frozen:
            raise TypeError(f"{name} is a read only attribute")
        super.__setattr__(self, name, value)

    def __delattr__(self, name: str):
        # can't delete non existing attributes
        if not hasattr(self, name):
            raise TypeError(f"{name} is not an attribute")
        # don't allow deleting mandatory attributes
        if _is_mandatory(self._convention[name]["flags"]) and self._frozen:
            raise TypeError(
                f"{name} is a mandatory attribute that can not be deleted")
        super().__delattr__(name)

    def info(self, info):
        """
        Print information about a SOFA object

        Parameters
        ----------
        info : str
            Specifies the kind of information that is printed:

            ``'all'``
                Print the name of all object attributes.
            ``'mandatory'``
                Print names of mandatory object attributes.
            ``'optional'``
                Print names of optional object attributes.
            ``'read only'``
                Print names of read only object attributes.
            ``'dimensions'``
                Print dimensions of the SOFA object.
            ``'type'``
                Print the data types of the object attributes
            ``'shape'``
                Print the shape object attributes if they are not None. The
                shape is given in the form of letters, e.g., `MRN`. These
                letters denote the dimensions of the SOFA object (see
                `dimensions` above).
            ``'comment'``
                Print the explanatory comments for the object attributes if
                they are not empty.
            ``'default'``
                Print the default values of the object attributes except for
                empty strings.
            key
                If key is the name of an object attribute, all information for
                attribute will be printed.

        Notes
        -----
        ``self.update_api(version='match')`` is called to make sure that the
        required meta data is available.

        """

        # update the API to make sure all meta data is in place
        self.update_api(version="match")

        # list of all attributes
        keys = [k for k in self.__dict__.keys() if not k.startswith("_")]

        # start printing the information
        info_str = (
            f"{self.GLOBAL_SOFAConventions} "
            F"{self.GLOBAL_SOFAConventionsVersion} "
            f"(SOFA version {self.GLOBAL_Version})\n")
        info_str += "-" * len(info_str) + "\n"

        if info == "dimensions":

            dimensions = {
                "M": "measurements",
                "N": "samples/frequencies/SOS coefficients/SH coefficients",
                "R": "receiver",
                "E": "emitter",
                "S": "maximum string length",
                "C": "coordinate dimensions, fixed",
                "I": "single dimension, fixed"}

            info_str += "Dimensions\n"
            for key, value in dimensions.items():
                info_str += f"\t{key} = {self._api[key]} ({value}))\n"

        elif info in ["all", "mandatory", "optional", "read only"]:

            info_str += f"{info} entries:\n"

            for key in keys:

                # check if field should be skipped
                flags = self._convention[key]["flags"]
                if (not _is_mandatory(flags) and info == "mandatory") \
                        or \
                        (_is_mandatory(flags) and info == "optional") \
                        or \
                        (not _is_read_only(flags) and info == "read only"):
                    continue

                info_str += key + "\n"

        elif info in ["read only", "type", "shape", "comment", "default"]:

            info_str += f"showing {info}:\n"

            if info == "shape":
                info = "dimensions"

            for key in keys:

                meta_data = self._convention[key][info]

                if meta_data is not None and meta_data != "":
                    if info == "dimensions":
                        meta_data = meta_data.upper()
                    info_str += f"{key}\n\t{meta_data}\n"

        elif info in keys:

            for key in [k for k in keys if info in k]:
                info_str += (
                    f"{key}\n"
                    f"\ttype: {self._convention[key]['type']}\n"
                    f"\tmandatory: "
                    f"{_is_mandatory(self._convention[key]['flags'])}\n"
                    f"\tread only: "
                    f"{_is_read_only(self._convention[key]['flags'])}\n"
                    f"\tdefault: {self._convention[key]['default']}\n"
                    f"\tshape: "
                    f"{str(self._convention[key]['dimensions']).upper()}\n"
                    f"\tcomment: {self._convention[key]['comment']}\n")
        else:
            raise ValueError(f"info='{info}' is invalid")

        print(info_str)

    def update_api(self, version="latest"):
        """
        Update the API of a SOFA object.

        The API contains meta data about the SOFA object, such as the type and
        default values of its attributes. It is required to show information
        about the SOFA object and to write a SOFA file to disk.

        .. note::
            ``update_api`` is automatically called when you create a new SOFA
            object or read a SOFA file disk using the default parameters.

        This function updates the API, checks if all mandatory fields are
        contained and if the dimensions of the data inside the SOFA object are
        according to the SOFA standard. If a mandatory attribute is missing, it
        is added to the SOFA object with its default value and a warning is
        raised.

        The API of a SOFA object contains of three parts, that are stored
        as private attributes. They should usually not be manipulated outside
        of `update_api`

        self._convention
            The SOFA convention with default values, variable dimensions, flags
            and comments. These data are read from the official SOFA
            conventions contained in the SOFA Matlab/Octave API
        self._dimensions
            The detected dimensions of the data inside the SOFA object
        self._api
            The size of the dimensions (see ``self.info("dimensions")``). This
            specifies the dimensions of the data inside the SOFA object.

        Parameters
        ----------
        version : str, optional
            The version to which the API is updated.

            ``'latest'``
                Use the latest API and upgrade the SOFA file if required.
            ``'match'``
                Match the version of the sofa file.
            str
                Version string, e.g., ``'1.0'``. Note that this might downgrade
                the SOFA object

            The default is ``'latest'``

        """

        # initialize the API
        self._add_api(version)
        self._frozen = False
        self._dimensions = {}
        self._api = {}
        self._frozen = True

        # first run: check if the mandatory attributes are contained
        keys = [key for key in self.__dict__.keys() if not key.startswith("_")]

        for key in self._convention.keys():
            if _is_mandatory(self._convention[key]["flags"]) \
                    and key not in keys:
                self._frozen = False
                setattr(self, self._convention[key]["default"])
                self._frozen = True
                warnings.warn((
                    f"Mandatory attribute {key} was missing and added to the "
                    "SOFA object with its default value"))

        # second run: Get the dimensions for E, R, M, N, and S
        keys = [key for key in self.__dict__.keys() if not key.startswith("_")
                and self._convention[key]["dimensions"] is not None]

        S = 0
        for key in keys:

            value = getattr(self, key)
            dimensions = self._convention[key]["dimensions"]

            for id, dim in enumerate(dimensions.split(", ")[0]):
                if dim in "ermn":
                    self._api[dim.upper()] = \
                        _nd_array(value, 4).shape[id]
                if dim == "S":
                    S = max(S,
                            _get_size_and_shape_of_string_var(value, key)[0])

        # add fixed sizes
        self._api["C"] = 3
        self._api["I"] = 1
        self._api["S"] = S

        # third run: verify dimensions of data
        for key in keys:

            # handle dimensions
            dimensions = self._convention[key]["dimensions"]

            # get value and actual shape
            try:
                value = getattr(self, key).copy()
            except AttributeError:
                value = getattr(self, key)

            if "S" in dimensions:
                # string or string array like data
                shape_act = _get_size_and_shape_of_string_var(value, key)[1]
            else:
                # array like data
                shape_act = _nd_array(value, 4).shape

            shape_matched = False
            for dim in dimensions.split(", "):

                # get the reference shape ('S' translates to a shape of 1,
                # because the strings are stored in an array whose shape does
                # not reflect the max. lengths of the actual strings inside it)
                shape_ref = tuple(
                    [self._api[d.upper()] if d != "S" else 1 for d in dim])

                # get shape for comparison to correct length by cropping and
                # appending singelton dimensions if required
                shape_compare = shape_act[:len(shape_ref)]
                for _ in range(len(shape_ref) - len(shape_compare)):
                    shape_compare += (1, )

                # check if the shapes match and write to API
                if shape_compare == shape_ref:
                    shape_matched = True
                    self._dimensions[key] = dim.upper()
                    break

            if not shape_matched:
                raise ValueError(
                    (f"The shape of {key} is {shape_compare} but has "
                     f"to be: {dimensions.upper()} "
                     "(see ``self.info('dimensions')`` and "
                     "``self.info('shape')``"))

    def _add_api(self, version):
        """
        Add API to SOFA object. If The SOFA files contains an API it is
        overwritten.

        Parameters
        ----------
        version : str
            ``'latest'``
                Use the latest API and upgrade the SOFA file if required.
            ``'match'``
                Match the version of the sofa file.
            str
                Version string, e.g., ``'1.0'``.
        """

        # load the desired convention and compare versions
        v_current = str(self.GLOBAL_SOFAConventionsVersion)
        if version == "match":
            version = v_current

        convention = self._load_convention(
            self.GLOBAL_SOFAConventions, version)
        v_new = str(float(
            convention["GLOBAL_SOFAConventionsVersion"]["default"]))

        if v_current != v_new:
            self._frozen = False
            self.GLOBAL_SOFAConventionsVersion = v_new
            self._frozen = True

        if float(v_current) < float(v_new):
            warnings.warn(("Upgraded SOFA object from "
                           f"version {v_current} to {v_new}"))
        elif float(v_current) > float(v_new):
            warnings.warn(("Downgraded SOFA object from "
                           f"version {v_current} to {v_new}"))

        # add convention
        self._convention = convention

    def _load_convention(self, convention, version):
        """
        Load SOFA convention from json file.

        Parameters
        ----------
        convention : str
            The name of the convention from which the SOFA file is created. See
            :py:func:`~sofar.list_conventions`.
        version : str
            ``'latest'``
                Use the latest API and upgrade the SOFA file if required.
            str
                Version string, e.g., ``'1.0'``.

        Returns
        -------
        convention : dict
            The SOFA convention as a dictionary
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

        # replace ':' and '.' in key names by '_'
        convention = {
            key.replace(':', '_'): value for key, value in convention.items()}
        convention = {
            key.replace('.', '_'): value for key, value in convention.items()}

        return convention

    def _convention2sofa(self,  mandatory):
        """
        Use SOFA convention to create attributes with default values.

        Parameters
        ----------
        mandatory : bool
            Flag to indicate if only mandatory fields are to be included.
        """

        # populate the SOFA file
        for key in self._convention.keys():

            # skip optional fields if requested
            if not _is_mandatory(self._convention[key]["flags"]) and mandatory:
                continue

            # get the default value
            default = self._convention[key]["default"]
            if isinstance(default, list):
                ndim = len(self._convention[key]["dimensions"].split(", ")[0])
                default = _nd_array(default, ndim)

            # create attribute with default value
            setattr(self, key, default)

        # write API and date specific fields (some read only)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._frozen = False
        self.GLOBAL_DateCreated = now
        self.GLOBAL_DateModified = now
        self.GLOBAL_APIName = "sofar SOFA API for Python (pyfar.org)"
        self.GLOBAL_APIVersion = sf.__version__
        self.GLOBAL_ApplicationName = "Python"
        self.GLOBAL_ApplicationVersion = platform.python_version()
        self._frozen = True


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

    .. note::
        If the official convention contain errors, calling this function might
        break sofar. Be sure that you want to do this.
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


def read_sofa(filename, update_api=True, version="latest"):
    """
    Read SOFA file from disk and convert it to SOFA object.

    Numeric data is returned as floats or numpy float arrays unless they have
    missing data, in which case they are returned as numpy masked arrays.

    Parameters
    ----------
    filename : str
        The filename. '.sofa' is appended to the filename, if it is not
        explicitly given.
    update_api : bool, optional
        Update the API by calling :py:func:`~Sofa.update_api`. This helps
        to find potential errors in the data and is thus recommended. If
        reading a file fails, try to call `read_sofa` with ``update=False``.
        The default is ``True``.
    version : str, optional
        The version to which the API is updated.

        ``'latest'``
            Use the latest API and upgrade the SOFA file if required.
        ``'match'``
            Match the version of the sofa file.
        str
            Version string, e.g., ``'1.0'``. Note that this might downgrade
            the SOFA object

        The default is ``'latest'``

    Returns
    -------
    sofa : Sofa
        The SOFA object filled with the default values of the convention.
    """

    # check the filename
    if not filename.lower().endswith('.sofa'):
        filename += ".sofa"
    if not os.path.isfile(filename):
        raise ValueError("{filename} does not exist")

    # open new NETCDF4 file for reading
    with Dataset(filename, "r", format="NETCDF4") as file:

        # get convention name and version
        convention = getattr(file, "SOFAConventions")
        read_version = getattr(file, "SOFAConventionsVersion")

        # get SOFA object with default values
        try:
            sofa = sf.Sofa(convention, version=read_version)
        except ValueError:
            try:
                warnings.warn((
                    f"No exact match found for {convention} {read_version}. "
                    "Trying to load latest version."))
                sofa = sf.Sofa(convention, version="latest")
            except ValueError:
                raise ValueError(
                    f"Convention {convention} is not included in sofar")
        convention = sofa._convention

        # allow writing read only attributes
        sofa._frozen = False

        # load global attributes
        for attr in file.ncattrs():
            setattr(sofa, "GLOBAL_" + attr, getattr(file, attr))

        # load data
        for var in file.variables.keys():
            # format and write value
            value = _format_value_from_netcdf(file[var][:], var)
            setattr(sofa, var.replace(".", "_"), value)

            # load variable attributes
            for attr in file[var].ncattrs():
                setattr(sofa, var.replace(".", "_") + "_" + attr,
                        getattr(file[var], attr))

        # do not allow writing read only attributes any more
        sofa._frozen = True

    # update api
    if update_api:
        try:
            sofa.update_api(version)
        except: # noqa (No error handling - just improved verbosity)
            raise ValueError((
                "The API could not be updated, maybe do to errornous data in "
                "the SOFA file. Tr to call sofa=sofar.read_sofa(filename, "
                "update=False) and than call sofar.update_api(sofa) to get "
                "more informations"))

    return sofa


def write_sofa(filename: str, sofa: Sofa, version="latest"):
    """
    Write a SOFA object to disk as a SOFA file.

    Parameters
    ----------
    filename : str
        The filename. '.sofa' is appended to the filename, if it is not
        explicitly given.
    sofa : dict
        The SOFA object that is written to disk
    version : str
        The SOFA API is updated with :py:func:`~Sofa.update_api` before writing
        to disk. Version specifies, which version of the convention is used.

        ``'latest'``
            Use the latest API and upgrade the SOFA file if required.
        ``'match'``
            Match the version of the sofa file.
        str
            Version string, e.g., ``'1.0'``.

        The default is ``'latest'``.
    """

    # check the filename
    if not filename.lower().endswith('.sofa'):
        filename += ".sofa"

    # update the dimensions
    sofa.update_api(version)

    # list of all attribute names
    all_keys = [key for key in sofa.__dict__.keys() if not key.startswith("_")]

    # open new NETCDF4 file for writing
    with Dataset(filename, "w", format="NETCDF4") as file:

        # write dimensions
        for dim in sofa._api:
            # Dimensions are stored in single upper case letter keys
            if len(dim) == 1:
                file.createDimension(dim, sofa._api[dim])

        # write global attributes
        keys = [key for key in all_keys if key.startswith("GLOBAL_")]
        for key in keys:
            setattr(file, key[7:], str(getattr(sofa, key)))

        # write data
        for key in all_keys:

            # skip attributes
            if ("_" in key and not key.startswith("Data_")) \
                    or key.count("_") > 1:
                continue

            # get the data and type and shape
            value, dtype = _format_value_for_netcdf(
                getattr(sofa, key), key, sofa._convention[key]["type"],
                sofa._dimensions[key], sofa._api["S"])

            # create variable and write data
            shape = tuple([dim for dim in sofa._dimensions[key]])
            tmp_var = file.createVariable(
                key.replace("Data_", "Data."), dtype, shape)
            try:
                tmp_var[:] = value
            except:  # noqa (this is no error handling just improved verbosity)
                shape_verbose = []
                for dim in sofa._dimensions[key]:
                    shape_verbose = shape_verbose.append(
                        dim + "=" + str(sofa._api[dim]))

                raise ValueError((
                    f"Error writing sofa.{key}: {value} of "
                    f"intended type '{dtype}' and shape {shape_verbose}"))

            # write variable attributes
            sub_keys = [k for k in all_keys if k.startswith(key + "_")]
            for sub_key in sub_keys:
                setattr(tmp_var, sub_key[len(key)+1:],
                        str(getattr(sofa, sub_key)))


def compare_sofa(sofa_a, sofa_b, verbose=True, exclude=None):
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
        is_identical = False
        if verbose:
            warnings.warn((
                f"not identical: sofa_a has {len(keys_a)} attributes for "
                f"comparison and sofa_b has {len(keys_b)}."))

        return is_identical

    # check if the keys match
    if set(keys_a) != set(keys_b):
        is_identical = False
        if verbose:
            warnings.warn(("not identical: sofa_a and sofa_b do not have the "
                           "same attributes"))

        return is_identical

    # compare attributes
    for key in [k for k in keys_a if
                sofa_a._convention[k]["type"] == "attribute"]:

        if str(getattr(sofa_a, key)) != str(getattr(sofa_b, key)):
            is_identical = False
            if verbose:
                warnings.warn(
                    f"not identical: different values for {key}")

    # compare data
    for key in [k for k in keys_a if
                sofa_a._convention[k]["type"] != "attribute"]:

        # get the values and copy them to avoid changing mutable objects
        a = getattr(sofa_a, key)
        b = getattr(sofa_b, key)
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
        The intended dimensions from ``sofa._dimensions``
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
    try:
        value = value.copy()
    except AttributeError:
        pass

    # parse data
    if dtype == "attribute":
        value = str(value)
        netcdf_dtype = "attribute"
    elif dtype == "double":
        value = _nd_array(value, len(dimensions))
        netcdf_dtype = "f8"
    elif dtype == "string":
        value = np.array(value, dtype="S" + str(S))
        value = _nd_array(value, len(dimensions))
        netcdf_dtype = 'S1'
    else:
        raise ValueError((
            f"Something went wrong in sofa.{key}. This is either a bug or an"
            "error in the convention."))

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


def _is_read_only(flags):
    """
    Check if a field is read only

    Parameters
    ----------
    flags : None, str
        The flags from convention[key]["flags"]

    Returns
    -------
    is_read_only : bool
    """
    # skip optional fields if requested
    if flags is None:
        is_read_only = False
    elif "r" not in flags:
        is_read_only = False
    else:
        is_read_only = True

    return is_read_only


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
