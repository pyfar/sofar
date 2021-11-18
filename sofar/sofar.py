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
from netCDF4 import Dataset, stringtochar
from copy import deepcopy
import sofar as sf


class Sofa():
    """Create a new SOFA object.

    Parameters
    ----------
    convention : str
        The name of the convention from which the SOFA file is created. See
        :py:func:`~sofar.list_conventions`.
    mandatory : bool, optional
        If ``True``, only the mandatory data of the convention will be
        returned. The default is ``False``, which returns mandatory and
        optional data.
    version : str, optional
        The version of the convention as a string, e.g., ``' 2.0'``. The
        default is ``'latest'``. Also see :py:func:`~sofar.list_conventions`.
    verify : bool, optional
        Verify the SOFA object by calling :py:func:`~Sofa.verify`. This helps
        to find potential errors in the default values and is thus recommended
        If creating a file does not work, try to call `Sofa` with
        ``verify=False``. The default is ``True``.

    Returns
    -------
    sofa : Sofa
        A SOFA object filled with the default values of the convention.

    Examples
    --------
    Create a new SOFA object with default values

    .. code-block:: python

        import sofar as sf

        # create SOFA object
        sofa = sf.Sofa("SimpleFreeFieldHRIR")

    Add data

    .. code-block:: python

        sofa.Data_IR = [1, 1]

    Data can be entered as numbers, numpy arrays or lists. Note the following
    if entering a list

    1. Lists are converted to a numpy array with at least two dimensions.
    2. Missing dimensions are appended when writing the SOFA object to disk.

    For more examples refer to the `Quick tour of SOFA and sofar` at
    https://sofar.readthedocs.io/en/latest/
    """

    # these have to be set here, because they are used in __setattr__ and
    # Python checks if they exist upon class creation

    # don't allow adding attributes and deleting/writing read only attributes
    _protected = False
    # list of read only attributes (filled upon init)
    _read_only_attr = []

    def __init__(self, convention, mandatory=False, version="latest",
                 verify=True):
        """See class docstring"""

        # get convention
        self._convention = self._load_convention(convention, version)

        # update read only attributes
        self._read_only_attr = [
            key for key in self._convention.keys()
            if self._read_only(self._convention[key]["flags"])]

        # add attributes with default values
        self._convention_to_sofa(mandatory)

        # add and update the API
        if verify:
            self.verify(version)

        self._protected = True

    def __setattr__(self, name: str, value):
        # don't allow new attributes to be added outside the class
        if self._protected and not hasattr(self, name):
            raise TypeError(f"{name} is an invalid attribute")

        # don't allow setting read only attributes
        if name in self._read_only_attr and self._protected:
            raise TypeError(f"{name} is a read only attribute")

        # convert to numpy array or scalar
        if not isinstance(value, (str, dict, np.ndarray)):
            value = np.atleast_2d(value)
            if value.size == 1:
                value = value.flatten()[0]

        super.__setattr__(self, name, value)

    def __delattr__(self, name: str):
        # can't delete non existing attributes
        if not hasattr(self, name):
            raise TypeError(f"{name} is not an attribute")
        # delete anything if not frozen, delete non mandatory
        if not self._protected or \
                not self._mandatory(self._convention[name]["flags"]):
            super().__delattr__(name)

            # check if custom field as to be deleted
            if hasattr(self, "_custom"):
                if name in self._custom:
                    self._custom.pop(name)
        else:
            raise TypeError(
                f"{name} is a mandatory attribute that can not be deleted")

    def __repr__(self):
        return (f"sofar.SOFA object: {self.GLOBAL_SOFAConventions} "
                f"{self.GLOBAL_SOFAConventionsVersion}")

    @property
    def list_dimensions(self):
        """
        Print the dimensions of the SOFA object

        The SOFA file standard defines the following dimensions:

        M
            number of measurements
        N
            number of samles, frequencies, SOS coefficients
            (depending on self.GLOBAL_DataType)
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

        see :py:func:`~Sofa.info` to see the shapes of the data inside the SOFA
        object.
        """

        # Check if the dimensions can be updated
        self._update_dimensions()

        # get verbose description for dimesion N
        if self.GLOBAL_DataType.startswith("FIR"):
            N_verbose = "samples"
        elif self.GLOBAL_DataType.startswith("TF"):
            N_verbose = "frequencies"
        elif self.GLOBAL_DataType.startswith("SOS"):
            N_verbose = "SOS coefficients"
        else:
            # This line can not be tested. An invalid DataType would be cached
            # in self.verify above. This to make sure we don't miss something
            # in case new DataTypes are added to SOFA in the future.
            raise ValueError((
                "GLOBAL_DataType start with 'FIR', 'TF', "
                f"or 'SOS' but not with {self.GLOBAL_DataType}"))

        # get verbose description for dimensions R and E
        R_verbose = "receiver spherical harmonics coefficients" if \
            'harmonic' in self.ReceiverPosition_Type else "receiver"
        E_verbose = "emitter spherical harmonics coefficients" if \
            'harmonic' in self.EmitterPosition_Type else "emitter"

        dimensions = {
            "M": "measurements",
            "N": N_verbose,
            "R": R_verbose,
            "E": E_verbose,
            "S": "maximum string length",
            "C": "coordinate dimensions, fixed",
            "I": "single dimension, fixed"}

        info_str = ""
        for key, value in self._api.items():
            dim_info = dimensions[key] if key in dimensions \
                else "custom dimension"

            info_str += f"{key} = {value} {dim_info}"

            if dim_info != "custom ":
                for key2, value2 in self._convention.items():
                    dim = value2["dimensions"]
                    if dim is not None and key.lower() in dim:
                        info_str += \
                            f" (set by {key2} of dimension {dim.upper()})"
                        break

            info_str += "\n"

        print(info_str)

    def get_dimension(self, dimension):
        """
        Get size of a SOFA dimension

        SOFA dimensions specify the shape of the data contained in a SOFA
        object. For a list of all dimensions see :py:func:`~list_dimensions`.

        Parameters
        ----------
        dimension : str
            The dimension as a string, e.g., ``'N'``.

        Returns
        -------
        size : int
            the size of the queried dimension.
        """

        # Check if the dimensions can be updated
        self._update_dimensions()

        if dimension not in self._api:
            raise ValueError((
                f"{dimension} is not a valid dimension. "
                "See Sofa.list_dimensions for a list of valid dimensions."))

        return self._api[dimension]

    def _update_dimensions(self):
        """
        Call verify and raise an error if the dimensions could not be updated.

        used in Sofa.list_dimensions and Sofa.get_dimension
        """

        issues = self.verify(version="match", issue_handling="return")
        if issues is not None and ("data of wrong type" in issues or
                                   "variables of wrong shape" in issues or
                                   not hasattr(self, "_api")):
            raise ValueError(("Dimensions can not be shown because variables "
                              "of wrong type or shape were detected. "
                              "Call Sofa.verify() for more information."))

    def info(self, info):
        """
        Print information about a SOFA object

        Parameters
        ----------
        info : str
            Specifies the kind of information that is printed:

            ``'all'`` ``'mandatory'`` ``'optional'`` ``'read only'`` ``'data'``
                Print the name, type, shape, and flags and comment for all or
                selected entries of the SOFA object. ``'data'`` does not show
                entries of type attribute.
            key
                If key is the name of an object attribute, all information for
                attribute will be printed.
        """

        # update the private attribute `_convention` to make sure the required
        # meta data is in place
        self._update_convention(version="match")

        # list of all attributes
        keys = [k for k in self.__dict__.keys() if not k.startswith("_")]

        # start printing the information
        info_str = (
            f"{self.GLOBAL_SOFAConventions} "
            F"{self.GLOBAL_SOFAConventionsVersion} "
            f"(SOFA version {self.GLOBAL_Version})\n")
        info_str += "-" * len(info_str) + "\n"

        if info in ["all", "mandatory", "optional", "read only", "data"]:

            info_str += f"showing {info} entries : type (shape), flags\n\n"

            for key in keys:

                # check if field should be skipped
                flags = self._convention[key]["flags"]
                if (not self._mandatory(flags) and info == "mandatory") \
                        or \
                        (self._mandatory(flags) and info == "optional") \
                        or \
                        (not self._read_only(flags) and info == "read only") \
                        or \
                        (self._convention[key]['type'] == "attribute" and
                         info == "data"):
                    continue

                info_str += f"{key} : {self._convention[key]['type']}"

                if self._convention[key]['dimensions']:
                    info_str += \
                        f" ({self._convention[key]['dimensions'].upper()})"

                if self._mandatory(flags):
                    info_str += ", mandatory"
                else:
                    info_str += ", optional"
                if self._read_only(flags):
                    info_str += ", read only"

                if self._convention[key]['comment']:
                    info_str += f"\n    {self._convention[key]['comment']}\n"
                else:
                    info_str += "\n"

        elif info in keys:

            for key in [k for k in keys if info in k]:
                comment = str(self._convention[key]['comment'])

                info_str += (
                    f"{key}\n"
                    f"    type: {self._convention[key]['type']}\n"
                    f"    mandatory: "
                    f"{self._mandatory(self._convention[key]['flags'])}\n"
                    f"    read only: "
                    f"{self._read_only(self._convention[key]['flags'])}\n"
                    f"    default: {self._convention[key]['default']}\n"
                    f"    shape: "
                    f"{str(self._convention[key]['dimensions']).upper()}\n"
                    f"    comment: {comment}\n")
        else:
            raise ValueError(f"info='{info}' is invalid")

        print(info_str)

    def add_variable(self, name, value, dtype, dimensions):
        """
        Add custom variable to the SOFA object, i.e., numeric or string arrays.

        Parameters
        ----------
        name : str
            Name of the new variable.
        value : any
            value to be added (see `dtype` for restrictions).
        dtype : str
            Type of the entry to be added in netCDF style:

            ``'double'``
                Use this to store numeric data that can be provided as number
                list or numpy array.
            ``'string'``
                Use this to store string variables as numpy string arrays of
                type ``'U'`` or ``'S'``.

        dimensions : str
            The shape of the new entry as a string. See
            ``self.info('dimensions')``.

        Examples
        --------
        .. code-block:: python

            import sofar as sf
            sofa = sf.Sofa("GeneralTF")

            # add numeric data
            sofa.add_variable("Temperature", 25.1, "double", "MI")

            # add GLOBAL and Variable attribtue
            sofa.add_entry(
                "GLOBAL_DateMeasured", "8.08.2021", "attribute", None)
            sofa.add_entry(
                "Temperature_Units", "degree Celsius", "attribute", None)

            # add a string data
            sofa.add_variable(
                "Comment", "Measured with wind screen", "string", "MS")
        """

        self._add_entry(name, value, dtype, dimensions)

    def add_attribute(self, name, value):
        """
        Add custom attribute to the SOFA object.

        Parameters
        ----------
        name : str
            Name of the new attribute.
        value : str
            value to be added.

        Examples
        --------
        .. code-block:: python

            import sofar as sf
            sofa = sf.Sofa("GeneralTF")

            # add GLOBAL and Variable attribtue
            sofa.add_attribute("GLOBAL_DateMeasured", "8.08.2021")
            sofa.add_attribute("Data_Real_Units", "Pascal")

        """

        self._add_entry(name, value, 'attribute', None)

    def _add_entry(self, name, value, dtype, dimensions):
        """
        Add custom data to a SOFA object. See add_variable and add_attribute
        for more information.
        """

        # check input
        if hasattr(self, name):
            raise ValueError(f"Entry {name} already exists")
        if dtype not in ["attribute", "double", "string"]:
            raise ValueError(
                f"dtype is {dtype} but must be attribute, double, or string")
        if "_" in name and dtype != "attribute":
            raise ValueError(("underscores '_' in the name are only "
                              "allowed for attributes"))
        if dtype == "attribute":
            if name.count("_") != 1 or \
                    (name.startswith("Data_") and (name.count("_") == 0 or
                                                   name.count("_") > 2)):
                raise ValueError((f"The name of {name} must have the "
                                  "form VariableName_AttributeName"))
            if not name.startswith("GLOBAL_") and \
                    name[:name.rindex("_")] not in self._convention:
                raise ValueError((f"Adding Attribute {name} requires "
                                  f"variable {name[:name.rindex('_')]}"))
        if dimensions is None and dtype != "attribute":
            raise ValueError(("dimensions must be provided for entries of "
                              "dtype double and string"))
        if dimensions is not None:
            dimensions = dimensions.upper()
            for dimension in dimensions:
                if dimension not in "ERMNCIS":
                    warnings.warn(
                        f"Added custom dimension {dimensions} to SOFA object")

        # add attribute to class
        _add_custom_api_entry(
            self, name, value, None, dimensions, dtype)

    def verify(self, version="latest", issue_handling="raise"):
        """
        Verify a SOFA object against the SOFA standard.

        This function updates the API, and checks the following

        - Are all mandatory fields contained? If not mandatory fields are added
          with their default value and a warning is raised.
        - Are the names of variables and attributes in accordance to the SOFA
          standard? If not a warning is raised.
        - Are the data types in accordance with the SOFA standard?
        - Are the dimensions of the variables consistent and in accordance
          to the SOFA standard?
        - Are the values of attributes consistent and in accordance to the
          SOFA standard?

        .. note::
            :py:func:`~verify` is automatically called when you create a new
            SOFA object, read a SOFA file from disk, and write a SOFA file to
            disk (using the default parameters).

        The API of a SOFA object consists of four parts, that are stored
        dictionaries in private attributes. This is required for writing data
        with :py:func:`~sofa.write_sofa` and should usually not be manipulated
        outside of :py:func:`~verify`

        self._convention
            The SOFA convention with default values, variable dimensions, flags
            and comments. These data are read from the official SOFA
            conventions contained in the SOFA Matlab/Octave API.
        self._dimensions
            The detected dimensions of the data inside the SOFA object.
        self._api
            The size of the dimensions (see py:func:`~list_dimensions`). This
            specifies the dimensions of the data inside the SOFA object.
        self._custom
            Stores information of custom variables that are not defined by the
            convention. The format is the same as in `self._convention`.

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
        issue_handling : str, optional
            Defines how detected issues are handeled

            ``'raise'``
                Warnings and errors are raised if issues are detected
            ``'print'``
                Issues are printed without raising warnings and errors
            ``'return'``
                Issues are returned as string but neither raised nor printed

            The default is ``'raise'``.

        Returns
        -------
        issues : str, None
            Detected issues as a string. None if no issues were detected. Note
            that this is only returned if ``issue_handling='return'`` (see
            above)

        """
        # NOTE: This function collects warnings and errors and tries to output
        # them in a block. This makes the code slightly more complicated but
        # is more convenient for the user and with respect to a potential
        # future web based tool for verifying SOFA files.

        # initialize warning and error messages
        error_msg = "\nERRORS\n------\n"
        warning_msg = "\nWARNINGS\n--------\n"

        # ---------------------------------------------------------------------
        # 0. update the convention
        self._update_convention(version)

        # ---------------------------------------------------------------------
        # 1. check if the mandatory attributes are contained
        current_warning = ""
        keys = [key for key in self.__dict__.keys() if not key.startswith("_")]

        for key in self._convention.keys():
            if self._mandatory(self._convention[key]["flags"]) \
                    and key not in keys:
                # add missing data with default value
                self._protected = False
                setattr(self, key, self._convention[key]["default"])
                self._protected = True

                # prepare to raise warning
                current_warning += "- " + key + "\n"

        if current_warning:
            warning_msg += "Added mandatory data with default values:\n"
            warning_msg += current_warning

        # ---------------------------------------------------------------------
        # 2. verify data type
        current_error = ""
        for key in keys:

            # handle dimensions
            dimensions = self._convention[key]["dimensions"]
            dtype = self._convention[key]["type"]

            # check data type
            value = getattr(self, key)

            if dtype == "attribute":
                if not isinstance(value, str):
                    current_error += \
                        f"- {key} must be string but is {type(value)}\n"

            elif dtype == "double":
                # multiple checks needed because sofar does not force the user
                # to initally pass data as numpy arrays
                if not isinstance(value,
                                  (np.int_, np.float_, np.double, np.ndarray)):
                    current_error += (f"- {key} must be int, float or numpy "
                                      f"array but is {type(value)}\n")

                if isinstance(value, np.ndarray) and not (
                        str(value.dtype).startswith('int') or
                        str(value.dtype).startswith('float')):
                    current_error += (f"- {key} must be int or float "
                                      f"but is {type(value.dtype)}\n")

            elif dtype == "string":
                # multiple checks needed because sofar does not force the user
                # to initally pass data as numpy arrays
                if not isinstance(value, (str, np.ndarray)):
                    current_error += (f"- {key} must be string or numpy array "
                                      f"but is {type(value)}\n")

                if isinstance(value, np.ndarray) and not (
                        str(value.dtype).startswith('<U') or
                        str(value.dtype).startswith('<S')):
                    current_error += (f"- {key} must be U or S "
                                      f"but is {type(value.dtype)}\n")

            else:
                # Could only be tested by manipulating JSON convention files
                # (Could take different data types in the future and convert to
                # numpy double arrays.)
                current_error += (
                    f"- {key}: Error in convention. Type must be "
                    f"double, string, or attribute but is {dtype}\n")

        if current_error:
            error_msg += "Detected data of wrong type:\n"
            error_msg += current_error

        # if an error ocurred up to here, it has to be handled. Otherwise
        # detecting the dimensions might fail. Warnings are not reported until
        # the end
        if error_msg != "\nERRORS\n------\n":
            _, issues = self._verify_handle_issues(
                    "\nWARNINGS\n--------\n", error_msg, issue_handling)

            if issue_handling == "print":
                return
            else:  # (issue_handling == "return"):
                return issues

        # ---------------------------------------------------------------------
        # 3. Verify names of entries

        # check attributes without variables
        current_error = ""
        for key in keys:

            if self._convention[key]["type"] != "attribute" or \
                    key.count("_") == 0:
                continue

            if (key[:key.rindex("_")] not in self._convention and
                    not key.startswith("GLOBAL_")):
                current_error += "- " + key + "\n"

        if current_error:
            error_msg += "Detected attributes with missing variables:\n"
            error_msg += current_error

        # check number of underscores
        current_error = ""
        for key in keys:

            if self._convention[key]["type"] != "attribute":
                continue

            # the case above caught attributes with too many underscores
            if key.count("_") == 0:
                current_error += "- " + key + "\n"

        if current_error:
            error_msg += (
                "Detected attribute names with too many or little underscores."
                " Names must have the form Variable_Attribute, Data_Attribute "
                "(one underscore), or Data_Variable_Attribute (two "
                "underscores):\n")
            error_msg += current_error

        # check numeric variables
        current_error = ""
        for key in keys:

            if self._convention[key]["type"] == "attribute":
                continue

            if "_" in key.replace("Data_", ""):
                current_error += "- " + key + "\n"

        if current_error:
            error_msg += (
                "Detected variable names with too many underscores."
                "Underscores are only allowed for the variable Data:\n")
            error_msg += current_error

        # ---------------------------------------------------------------------
        # 4. Get dimensions (E, R, M, N, S, c, I, and custom)

        # initialize required API fields
        self._protected = False
        self._dimensions = {}
        self._api = {}
        self._protected = True

        # get keys for checking the dimensions (all SOFA variables)
        keys = [key for key in self.__dict__.keys()
                if key in self._convention
                and self._convention[key]["dimensions"] is not None]
        if hasattr(self, "_custom"):
            keys_custom = [key for key in self._custom.keys()
                           if not key.startswith("_")
                           and self._custom[key]["dimensions"] is not None]
            keys += keys_custom

        S = 0
        for key in keys:

            value = getattr(self, key)
            dimensions = self._convention[key]["dimensions"]

            # - dimensions are given as string, e.g., 'mRN', or 'IC, MC'
            # - defined by lower case letters in `dimensions`
            for id, dim in enumerate(dimensions.split(", ")[0]):
                if dim not in "ICS" and dim.islower():
                    # numeric data
                    self._api[dim.upper()] = \
                        _nd_newaxis(value, 4).shape[id]
                if dim == "S":
                    # string data
                    S = max(S, np.max(self._get_size_and_shape_of_string_var(
                        value, key)[0]))

        # add fixed sizes
        self._api["C"] = 3
        self._api["I"] = 1
        self._api["S"] = S

        # ---------------------------------------------------------------------
        # 5. verify dimensions of data
        current_error = ""
        for key in keys:

            # handle dimensions
            dimensions = self._convention[key]["dimensions"]
            dtype = self._convention[key]["type"]

            # get value and actual shape
            try:
                value = getattr(self, key).copy()
            except AttributeError:
                value = getattr(self, key)

            if dtype in ["attribute", "string"]:
                # string or string array like data
                shape_act = self._get_size_and_shape_of_string_var(
                    value, key)[1]
            elif len(dimensions.split(",")[0]) > 1:
                # multidimensional array like data
                shape_act = _atleast_nd(value, 4).shape
            else:
                # scalar of single dimensional array like data
                shape_act = (np.array(value).size, )

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
                # get possible dimensions in verbose form, i.e., "(M=2, C=3)""
                dimensions_verbose = []
                for dim in dimensions.upper().replace(" ", "").split(","):
                    dimensions_verbose.append(
                        f"({', '.join([f'{d}={self._api[d]}' for d in dim])})")

                current_error += (
                    f"- {key} has shape {shape_compare} but must "
                    f"have {', '.join(dimensions_verbose)}\n")

        if current_error:
            error_msg += "Detected variables of wrong shape:\n"
            error_msg += current_error

        # ---------------------------------------------------------------------
        # 6. check restrictions on the content of SOFA files
        data, data_type, api, convention, unit_aliases = _sofa_restrictions()

        # general restrictions on data
        current_error = ""
        for key in data.keys():

            ref = data[key]["value"]
            if hasattr(self, key):

                # test if the value is valid
                test = getattr(self, key)
                if not self._verify_value(test, ref, unit_aliases):
                    current_error += \
                        f"- {key} is {test} but must be {', '.join(ref)}\n"

                # check dependencies
                if "dependency" not in data[key]:
                    continue

                for key_dep, ref_dep in data[key]["dependency"].items():

                    # check if dependency is contained in SOFA object
                    # hard to test, because mandatory fields are added by sofar
                    # this is more to be future proof
                    if not hasattr(self, key_dep):
                        current_error += (f"- {key_dep} must be given if "
                                          f"{key} is in SOFA object\n")
                        continue

                    # check if dependency has the correct value
                    test_dep = getattr(self, key_dep)
                    if not (isinstance(ref, list) and
                            isinstance(ref_dep, list)):
                        continue

                    idx = ref.index(test)
                    if not self._verify_value(test_dep, ref_dep[idx],
                                              unit_aliases):
                        current_error += (
                            f"- {key_dep} is {test_dep} but must be "
                            f"{ref_dep[idx]} if {key} is {test}\n")

        # restriction posed by GLOBAL_DataType
        if self.GLOBAL_DataType.startswith("FIR"):
            data_str = "FIR"
        elif self.GLOBAL_DataType.startswith("TF"):
            data_str = "TF"
        elif self.GLOBAL_DataType.startswith("SOS"):
            data_str = "SOS"
        else:
            # the data type was tested before. This is to prevent redundant
            # errors in the next for loop
            data_str = False

        if data_str:
            for key, value in data_type[data_str].items():

                # hard to test. included to detect problems with future
                # conventions
                if not hasattr(self, key):
                    current_error += (
                        f"- {key} must be contained if"
                        f" GLOBAL_DataType={self.GLOBAL_DataType}\n")

                if value is not None and getattr(self, key) not in value[0]:
                    current_error += (f"{key} is {getattr(self, key)} but "
                                      f"must be {value[1]}\n")

        # restrictions on the API
        for key, value in api.items():
            if hasattr(self, key) and getattr(self, key) == value["value"]:
                size = getattr(self, "_api")[value["API"][0]]
                if size not in value["API"][1]:
                    current_error += \
                        (f"- Dimension {value['API'][0]} is of size {size} "
                         f"but must be {value['API'][2]} if "
                         f"{key} is {getattr(self, key)}\n")

        # restrictions from the SOFA convention (on the data and API)
        if self.GLOBAL_SOFAConventions in convention:
            for key, ref in convention[self.GLOBAL_SOFAConventions].items():

                if key == "API":
                    for dimension, size in ref.items():
                        if self._api[dimension] != size:
                            current_error += \
                    (f"- Dimension {dimension} is of size "  # noqa
                     f"{self._api[dimension]} but must be {size} if "
                     f"GLOBAL_SOFAConventions is {key}\n")
                else:
                    value = getattr(self, key)
                    if value not in ref:
                        current_error += \
                            f"{key} is {value} but must be {ref}\n"

        if current_error:
            error_msg += "Detected violations of the SOFA convention:\n"
            error_msg += current_error

        # handle warnings and errors
        error_occurred, issues = self._verify_handle_issues(
                warning_msg, error_msg, issue_handling)

        if error_occurred:
            if issue_handling == "print":
                return
            elif issue_handling == "return":
                return issues

    @staticmethod
    def _verify_value(test, ref, unit_aliases):
        """
        Check a value agains the SOFA standard for Sofa.verify()

        Parameters
        ----------
        test :
            the value under test
        ref :
            the value enforced by the SOFA standard
        unit_aliases :
            dict of aliases for units from _sofa_restrictions()

        Returns
        -------
        ``True`` if `test` and `ref` agree, ``False`` otherwise
        """

        value_valid = True

        # Don't check the value if ref is None or test in ref
        if ref is not None and test not in ref:

            # in case test is a string it might be a unit and unit aliases
            # according to the SOFA standard must be checked
            units = test.split(", ") if isinstance(test, str) else []
            ref = ref.split(", ") if isinstance(ref, str) else ref

            if not units or len(ref) != len(units):
                value_valid = False
                return value_valid

            for unit, unit_ref in zip(units, ref):
                if unit != unit_ref and (unit not in unit_aliases
                                         or unit_aliases[unit] != unit_ref):
                    value_valid = False
                    break

        return value_valid

    @staticmethod
    def _verify_handle_issues(warning_msg, error_msg, issue_handling):
        """Handle warnings and errors from Sofa.verify"""

        # handle warnings
        if warning_msg != "\nWARNINGS\n--------\n":
            if issue_handling == "raise":
                warnings.warn(warning_msg)
            elif issue_handling == "print":
                print(warning_msg)
        else:
            warning_msg = None

        # handle errors
        if error_msg != "\nERRORS\n------\n":
            if issue_handling == "raise":
                raise ValueError(error_msg)
            elif issue_handling == "print":
                print(error_msg)
        else:
            error_msg = None

        # flag indicating if an error occurred
        error_occurred = error_msg is not None

        # verbose issue message
        if warning_msg and error_msg:
            issues = error_msg + "\n" + warning_msg
        elif warning_msg:
            issues = warning_msg
        elif error_msg:
            issues = error_msg
        else:
            issues = None

        return error_occurred, issues

    def copy(self):
        """Return a copy of the SOFA object."""
        return deepcopy(self)

    def _update_convention(self, version):
        """
        Add SOFA convention to SOFA object in private attribute `_convention`.
        If The object already contains a convention, it will be overwritten.

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

        # verify convention and version
        c_current = self.GLOBAL_SOFAConventions
        v_current = str(self.GLOBAL_SOFAConventionsVersion)

        v_new = _verify_convention_and_version(
                version, v_current, c_current)

        # load and add convention and version
        convention = self._load_convention(
            c_current, v_new)
        self._convention = convention

        if v_current != v_new:
            self._protected = False
            self.GLOBAL_SOFAConventionsVersion = v_new
            self._protected = True

        # feedback in case of up/downgrade
        if float(v_current) < float(v_new):
            warnings.warn(("Upgraded SOFA object from "
                           f"version {v_current} to {v_new}"))
        elif float(v_current) > float(v_new):
            warnings.warn(("Downgraded SOFA object from "
                           f"version {v_current} to {v_new}"))

        # check if custom fields can be added
        if hasattr(self, "_custom"):
            for key in self._custom:
                self._convention[key] = self._custom[key]

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
            raise TypeError(("Convention must be a string "
                             f"but is of type {type(convention)}"))

        # get and check path to json file
        paths = _get_conventions("path")
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

    def _convention_to_sofa(self, mandatory):
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
            if not self._mandatory(self._convention[key]["flags"]) \
                    and mandatory:
                continue

            # get the default value
            default = self._convention[key]["default"]
            if isinstance(default, list):
                ndim = len(self._convention[key]["dimensions"].split(", ")[0])
                default = _atleast_nd(default, ndim)

            # create attribute with default value
            setattr(self, key, default)

        # write API and date specific fields (some read only)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._protected = False
        self.GLOBAL_DateCreated = now
        self.GLOBAL_DateModified = now
        self.GLOBAL_APIName = "sofar SOFA API for Python (pyfar.org)"
        self.GLOBAL_APIVersion = sf.__version__
        self.GLOBAL_ApplicationName = "Python"
        self.GLOBAL_ApplicationVersion = (
            f"{platform.python_version()} "
            f"[{platform.python_implementation()} - "
            f"{platform.python_compiler()}]")
        self._protected = True

    @staticmethod
    def _get_size_and_shape_of_string_var(value, key):
        """
        String variables can be strings, list of strings, or numpy arrays of
        strings. This functions returns the length of the longest string S
        inside the string variable and the shape of the string variable as
        required by the SOFA definition. Note that the shape is the shape of
        the array that holds the strings. NETCDF stores all string variables in
        arrays.
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
            raise TypeError((f"{key} must be a string, numpy string array, "
                             "or list of strings"))

        return S, shape

    @staticmethod
    def _mandatory(flags):
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

    @staticmethod
    def _read_only(flags):
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


def _update_conventions(conventions_path=None):
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

    Parameters
    ----------
    conventions_path : str, optional
        Path to the folder where the conventions are saved. The default is
        ``None``, which saves the conventions inside the sofar package.
        Conventions saved under a different path can not be used by sofar.
    """

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

    # Loop conventions
    updated = False
    for convention in conventions:

        # exclude these conventions
        if convention.startswith(("General_", "GeneralString_")):
            continue

        filename_csv = os.path.join(conventions_path, "source", convention)
        filename_json = os.path.join(conventions_path, convention[:-3]+"json")

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

        # convert SOFA conventions from csv to json
        convention_dict = _convention_csv2dict(filename_csv)

        with open(filename_json, 'w') as file:
            json.dump(convention_dict, file, indent=4)

    if updated:
        print("... done.")
    else:
        print("... conventions already up to date.")


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
            files
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
    directory = os.path.join(os.path.dirname(__file__), "conventions")

    # SOFA convention files
    paths = [file for file in glob.glob(os.path.join(directory, "*.json"))]

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
    elif return_type == "path":
        return paths
    elif return_type == "name":
        return conventions
    elif return_type == "name_version":
        return [(n, v) for n, v in zip(conventions, versions)]
    elif return_type == "string":
        return conventions_str
    else:
        raise ValueError(f"return_type {return_type} is invalid")


def read_sofa(filename, verify=True, version="latest"):
    """
    Read SOFA file from disk and convert it to SOFA object.

    Numeric data is returned as floats or numpy float arrays unless they have
    missing data, in which case they are returned as numpy masked arrays.

    Parameters
    ----------
    filename : str
        The filename. '.sofa' is appended to the filename, if it is not
        explicitly given.
    verify : bool, optional
        Verify and update the SOFA object by calling :py:func:`~Sofa.verify`.
        This helps to find potential errors in the default values and is thus
        recommended. If reading a file does not work, try to call `Sofa` with
        ``verify=False``. The default is ``True``.
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
    if not filename.endswith('.sofa'):
        raise ValueError("Filename must end with .sofa")
    if not os.path.isfile(filename):
        raise ValueError(f"{filename} does not exist")

    # attributes that are skipped
    skip = ["_Encoding"]

    # init list of custom attributes
    custom = []

    # open new NETCDF4 file for reading
    with Dataset(filename, "r+", format="NETCDF4") as file:

        # get convention name and version
        convention = getattr(file, "SOFAConventions")
        version_in = getattr(file, "SOFAConventionsVersion")

        # check if convention and version exist
        try:
            version_out = _verify_convention_and_version(
                version, version_in, convention)
        except ValueError as ve:
            if "Convention" in str(ve):
                raise ValueError(f"File has unknown convention {convention}")
            else:
                raise ValueError("Version not found. Try version=latest")

        # get SOFA object with default values
        sofa = sf.Sofa(convention, version=version_out, verify=verify)

        # allow writing read only attributes
        sofa._protected = False

        # load global attributes
        for attr in file.ncattrs():

            value = getattr(file, attr)

            if not hasattr(sofa, "GLOBAL_" + attr):
                _add_custom_api_entry(sofa, "GLOBAL_" + attr, value, None,
                                      None, "attribute")
                custom.append("GLOBAL_" + attr)
                sofa._protected = False
            else:
                setattr(sofa, "GLOBAL_" + attr, value)

        # load data
        for var in file.variables.keys():

            # for automatic conversion of string variables
            if file[var].dtype == "S1":
                file[var]._Encoding = "ascii"

            value = _format_value_from_netcdf(file[var][:], var)

            if hasattr(sofa, var.replace(".", "_")):
                setattr(sofa, var.replace(".", "_"), value)
            else:
                dimensions = "".join([d for d in file[var].dimensions])
                # SOFA only uses dtypes 'double' and 'S1' but netCDF has more
                dtype = "string" if file[var].datatype == "S1" else "double"
                _add_custom_api_entry(sofa, var.replace(".", "_"), value, None,
                                      dimensions, dtype)
                custom.append(var.replace(".", "_"))
                sofa._protected = False

            # load variable attributes
            for attr in [a for a in file[var].ncattrs() if a not in skip]:

                value = getattr(file[var], attr)

                if not hasattr(sofa, var.replace(".", "_") + "_" + attr):
                    _add_custom_api_entry(
                        sofa, var.replace(".", "_") + "_" + attr, value, None,
                        None, "attribute")
                    custom.append(var.replace(".", "_") + "_" + attr)
                    sofa._protected = False
                else:
                    setattr(sofa, var.replace(".", "_") + "_" + attr, value)

        # do not allow writing read only attributes any more
        sofa._protected = True

    # notice about custom entries
    if custom:
        warnings.warn(("SOFA file contained custom entries "
                      f"({', '.join(custom)})"))

    # update api
    if verify:
        try:
            sofa.verify(version)
        except: # noqa (No error handling - just improved verbosity)
            raise ValueError((
                "The SOFA object could not be verified, maybe due to errornous"
                " data. Call sofa=sofar.read_sofa(filename, verify=False) and "
                "than sofa.verify() to get more information"))

    return sofa


def write_sofa(filename: str, sofa: Sofa, version="latest", compression=4):
    """
    Write a SOFA object to disk as a SOFA file.

    Parameters
    ----------
    filename : str
        The filename. '.sofa' is appended to the filename, if it is not
        explicitly given.
    sofa : object
        The SOFA object that is written to disk
    version : str
        The SOFA object is verified and updated with :py:func:`~Sofa.verify`
        before writing to disk. Version specifies, which version of the
        convention is used:

        ``'latest'``
            Use the latest version upgrade the SOFA file if required.
        ``'match'``
            Match the version of the SOFA object.
        str
            Version string, e.g., ``'1.0'``.

        The default is ``'latest'``.
    compression : int
        The level of compression with ``0`` being no compression and ``9``
        being the best compression. The default of ``9`` optimizes the file
        size but increases the time for writing files to disk.
    """

    # check the filename
    if not filename.endswith('.sofa'):
        raise ValueError("Filename must end with .sofa")

    # setting the netCDF compression parameter
    zlib = False if compression == 0 else True

    # update the dimensions
    sofa.verify(version)

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
            shape = tuple([dim for dim in sofa._dimensions[key]])
            tmp_var = file.createVariable(
                key.replace("Data_", "Data."), dtype, shape,
                zlib=zlib, complevel=compression)
            if dtype == "f8":
                tmp_var[:] = value
            else:
                tmp_var[:] = stringtochar(value)
                tmp_var._Encoding = "ascii"

            # write variable attributes
            sub_keys = [k for k in all_keys if k.startswith(key + "_")]
            for sub_key in sub_keys:
                setattr(tmp_var, sub_key[len(key)+1:],
                        str(getattr(sofa, sub_key)))


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
    try:
        value = value.copy()
    except AttributeError:
        pass

    # parse data
    if dtype == "attribute":
        value = str(value)
        netcdf_dtype = "attribute"
    elif dtype == "double":
        value = _atleast_nd(value, len(dimensions))
        netcdf_dtype = "f8"
    elif dtype == "string":
        value = np.array(value, dtype="S" + str(S))
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
    elif str(value.dtype)[1] == "S" or str(value.dtype)[1] == "U":
        # string arrays are stored in masked arrays with empty strings '' being
        # masked. Convert to regular arrays with unmasked empty strings
        value = np.asarray(value).astype("U")
    else:
        raise TypeError(
            f"{key}: value.dtype is {value.dtype} but must be float, S or, U")

    # convert arrays to scalars if they do not store data that is usually used
    # as scalar metadata, e.g., the SamplingRate
    data_keys = ["Data_IR", "Data_Real", "Data_Imag", "Data_SOS" "Data_Delay"]
    if value.size == 1 and key not in data_keys:
        value = value[0]

    return value


def _add_custom_api_entry(sofa, key, value, flags, dimensions, dtype):
    """
    Add custom entry to the sofa._convention and permanently save it in
    sofa._custom

    Parameters
    ----------
    sofa : Sofa
    key : str
        name of the entry
    flags, dimensions, dtype : any
        as in sofa._convention
    """
    # create custom API if it not exists
    sofa._protected = False
    if not hasattr(sofa, "_custom"):
        sofa._custom = {}

    # lower case letters to indicate custom dimensions
    if dimensions is not None:
        dimensions = [d.upper() if d.upper() in "ERMNCIS" else d.lower()
                      for d in dimensions]
        dimensions = "".join(dimensions)

    # add user entry to custom API
    sofa._custom[key] = {
        "flags": flags,
        "dimensions": dimensions,
        "type": dtype,
        "default": None,
        "comment": ""}
    sofa._update_convention(version="match")

    # add attribute to object
    setattr(sofa, key, value)
    sofa._protected = True


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
            f"Convention {convention} does not exist")

    name_version = _get_conventions("name_version")

    if version == "latest":
        # get list of versions as floats
        version_out = [float(versions[1]) for versions in name_version
                       if versions[0] == convention]
        # get latest version as string
        version_out = str(version_out[np.argmax(version_out)])
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
            raise ValueError(
                f"Version {match} does not exist. Try version='latest'")

    return version_out


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


def _sofa_restrictions():
    """
    Return dictionaries to check restrictions on the data posed by SOFA.

    The check is done in SOFA.verify(). This is not a private class method,
    to save additional indention that would make the code harder to read and
    write.

    Returns:
    data : dict
        General restrictions on the data of any SOFA convention
    data_type : dict
        Restriction depending on GLOBAL_DataType
    api : dict
        Restrictions on the API depending on specific fields of a SOFA file
    """

    # definition of valid coordinate systems and units
    coords_min = ["cartesian", "spherical"]
    coords_full = coords_min + ["spherical harmonics"]
    units_min = ["metre", "degree, degree, metre"]
    units_full = units_min + [units_min[1]]
    unit_aliases = {
        "metres": "metre",
        "meter": "metre",
        "meters": "metre",
        "cubic metres": "cubic metre",
        "cubic meter": "cubic metre",
        "cubic meters": "cubic metre",
        "degrees": "degree",
        "seconds": "second"
    }
    # possible values for restricted dimensions in the API
    sh_dimension = ([(N+1)**2 for N in range(200)],
                    "(N+1)**2 where N is the spherical harmonics order")
    sos_dimension = ([6 * (N + 1) for N in range(1000)],
                     "an integer multiple of 6 greater 0")

    # restrictions on the data
    # - if `value` is None it in only checked if the SOFA object has the attr
    # - if `value` is a list, it is also checked if the actual value is in
    #   `value`
    # - if there is a list of values for a dependency the value of the SOFA
    #   object has to match the value of the list at a certain index. The index
    #   is determined by the value of the parent.
    data = {
        # Global --------------------------------------------------------------
        # GLOBAL_SOFAConventions?
        # Check value of GLOBAL_DataType
        # (FIRE and TFE are legacy data types from SOFA version 1.0)
        "GLOBAL_DataType": {
            "value": ["FIR", "FIR-E", "FIRE", "TF", "TF-E", "TFE", "SOS"]},
        "GLOBAL_RoomType": {
            "value": ["free field", "reverberant", "shoebox", "dae"]},
        "GLOBAL_SOFAConventions": {
            "value": _get_conventions(return_type="name")},
        # Listener ------------------------------------------------------------
        # Check values and consistency of if ListenerPosition Type and Unit
        "ListenerPosition_Type": {
            "value": coords_min,
            "dependency": {
                "ListenerPosition_Units": units_min}},
        # Check if dependencies of ListenerView are contained
        "ListenerView": {
            "value": None,
            "dependency": {
                "ListenerView_Type": None,
                "ListenerView_Units": None}},
        # Check values and consistency of if ListenerView Type and Unit
        "ListenerView_Type": {
            "value": coords_min,
            "dependency": {
                "ListenerView_Units": units_min}},
        # Check if dependencies of ListenerUp are contained
        "ListenerUp": {
            "value": None,
            "dependency": {
                "ListenerView": None}},
        # Receiver ------------------------------------------------------------
        # Check values and consistency of if ReceiverPosition Type and Unit
        "ReceiverPosition_Type": {
            "value": coords_full,
            "dependency": {
                "ReceiverPosition_Units": units_full}},
        # Check if dependencies of ReceiverView are contained
        "ReceiverView": {
            "value": None,
            "dependency": {
                "ReceiverView_Type": None,
                "ReceiverView_Units": None}},
        # Check values and consistency of if ReceiverView Type and Unit
        "ReceiverView_Type": {
            "value": coords_min,
            "dependency": {
                "ReceiverView_Units": units_min}},
        # Check if dependencies of ReceiverUp are contained
        "ReceiverUp": {
            "value": None,
            "dependency": {
                "ReceiverView": None}},
        # Source --------------------------------------------------------------
        # Check values and consistency of if SourcePosition Type and Unit
        "SourcePosition_Type": {
            "value": coords_min,
            "dependency": {
                "SourcePosition_Units": units_min}},
        # Check if dependencies of SourceView are contained
        "SourceView": {
            "value": None,
            "dependency": {
                "SourceView_Type": None,
                "SourceView_Units": None}},
        # Check values and consistency of if SourceView Type and Unit
        "SourceView_Type": {
            "value": coords_min,
            "dependency": {
                "SourceView_Units": units_min}},
        # Check if dependencies of SourceUp are contained
        "SourceUp": {
            "value": None,
            "dependency": {
                "SourceView": None}},
        # Emitter -------------------------------------------------------------
        # Check values and consistency of if EmitterPosition Type and Unit
        "EmitterPosition_Type": {
            "value": coords_full,
            "dependency": {
                "EmitterPosition_Units": units_full}},
        # Check if dependencies of EmitterView are contained
        "EmitterView": {
            "value": None,
            "dependency": {
                "EmitterView_Type": None,
                "EmitterView_Units": None}},
        # Check values and consistency of if EmitterView Type and Unit
        "EmitterView_Type": {
            "value": coords_min,
            "dependency": {
                "EmitterView_Units": units_min}},
        # Check if dependencies of EmitterUp are contained
        "EmitterUp": {
            "value": None,
            "dependency": {
                "EmitterView": None}},
        # Room ----------------------------------------------------------------
        "RoomVolume": {
            "value": None,
            "dependency": {
                "RoomVolume_Units": None}},
        "RoomTemperature": {
            "value": None,
            "dependency": {
                "RoomTemperature_Units": None}},
        "RoomVolume_Units": {
            "value": ["cubic metre"]},
        "RoomTemperature_Units": {
            "value": ["Kelvin"]}
    }

    # restrictions arising from GLOBAL_DataType
    # - if `value` is None it is only checked if the SOFA object has the attr
    # - if `value` is a list, it is also checked if the actual value is in
    #   `value`
    data_type = {
        "FIR": {
            "Data_IR": None,
            "Data_Delay": None,
            "Data_SamplingRate": None,
            "Data_SamplingRate_Units": (["hertz"], "hertz")},
        "TF": {
            "Data_Real": None,
            "Data_Imag": None,
            "N": None,
            "N_LongName": (["frequency"], "frequency"),
            "N_Units": (["hertz"], "hertz")},
        "SOS": {
            "Data_SOS": None,
            "Data_Delay": None,
            "Data_SamplingRate": None,
            "Data_SamplingRate_Units": (["hertz"], "hertz")}
    }

    # restrictions on the API
    api = {
        # Check dimension R if using spherical harmonics for the Receiver
        # (assuming SH orders < 200)
        "ReceiverPosition_Type": {
            "value": "spherical harmonics",
            "API": ("R", ) + sh_dimension},
        # Check dimension E if using spherical harmonics for the Emitter
        # (assuming SH orders < 200)
        "EmitterPosition_Type": {
            "value": "spherical harmonics",
            "API": ("E", ) + sh_dimension},
        # Checking the dimension of N if having SOS data
        # (assuming up to 1000 second order sections)
        "GLOBAL_DataType": {
            "value": "SOS",
            "API": ("N", ) + sos_dimension}
    }

    # restrictions from the convention. Values of fields will be checked.
    # Must contain testing the API. If this would be tested under api={}, the
    # entry GLOBAL_SOFAConventions would be repeated.
    convention = {
        "GeneralFIR": {
            "GLOBAL_DataType": ["FIR"]},
        "GeneralFIR-E": {
            "GLOBAL_DataType": ["FIR-E"]},
        "GeneralFIRE": {  # SOFA version 1.0 legacy
            "GLOBAL_DataType": ["FIRE"]},
        "GeneralTF": {
            "GLOBAL_DataType": ["TF"]},
        "GeneralTF-E": {
            "GLOBAL_DataType": ["TF-E"]},
        "SimpleFreeFieldHRIR": {
            "GLOBAL_DataType": ["FIR"],
            "GLOBAL_RoomType": ["free field"],
            "EmitterPosition_Type": coords_min,
            "API": {"E": 1}},
        "SimpleFreeFieldHRTF": {
            "GLOBAL_DataType": ["TF"],
            "GLOBAL_RoomType": ["free field"],
            "EmitterPosition_Type": coords_min,
            "API": {"E": 1}},
        "SimpleFreeFieldHRSOS": {
            "GLOBAL_DataType": ["SOS"],
            "GLOBAL_RoomType": ["free field"],
            "EmitterPosition_Type": coords_min,
            "API": {"E": 1}},
        "FreeFieldHRIR": {
            "GLOBAL_DataType": ["FIR-E"],
            "GLOBAL_RoomType": ["free field"]},
        "FreeFieldHRTF": {
            "GLOBAL_DataType": ["TF-E"],
            "GLOBAL_RoomType": ["free field"]},
        "SimpleHeadphoneIR": {
            "GLOBAL_DataType": ["FIR"]},
        "SingleRoomSRIR": {
            "GLOBAL_DataType": ["FIR"]},
        "SingleRoomMIMOSRIR": {
            "GLOBAL_DataType": ["FIR-E"]},
        "FreeFieldDirectivityTF": {
            "GLOBAL_DataType": ["TF"]}
    }

    return data, data_type, api, convention, unit_aliases
