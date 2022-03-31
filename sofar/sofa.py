import os
import re
import json
from datetime import datetime
import platform
import numpy as np
import warnings
from copy import deepcopy
import sofar as sf
from .utils import (_nd_newaxis, _atleast_nd, _get_conventions,
                    _verify_convention_and_version)


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

    Add data as a list

    .. code-block:: python

        sofa.Data_IR = [1, 1]

    Data can be entered as numbers, numpy arrays or lists. Note the following

    1. Lists are converted to numpy arrays with at least two dimensions, i.e.,
       ``sofa.Data_IR`` is converted to a numpy array of shape (1, 2)
    2. Missing dimensions are appended when writing the SOFA object to disk,
       i.e., ``sofa.Data_IR`` is written as an array of shape (1, 2, 1) because
       the SOFA standard AES69-2020 defines it as a three dimensional array
       with the dimensions (`M: measurements`, `R: receivers`, `N: samples`)
    3. When reading data from a SOFA file, array data is always returned as
       numpy arrays and singleton trailing dimensions are discarded (numpy
       default). I.e., ``sofa.Data_IR`` will again be an array of shape (1, 2)
       after writing and reading to and from disk.
    4. One dimensional arrays with only one element will be converted to scalar
       values. E.g. ``sofa.Data_SamplingRate`` is stored as an array of shape
       (1, ) inside SOFA files (according to the SOFA standard AES69-2020) but
       will be a scalar inside SOFA objects after reading from disk.


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
        # (mandatory=True can not be verified because some conventions have
        # default values that have optional variables as dependencies)
        if verify and not mandatory:
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

        See :py:func:`~Sofa.inspect` to see the shapes of the data inside the
        SOFA object and :py:func:`~Sofa.get_dimension` to get the size/value
        of a specific dimensions as integer number.

        The SOFA file standard defines the following dimensions that are used
        to define the shape of the data entries:

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
        Print information about the convention of a SOFA object.

        Prints the variable type (attribute, double, string), shape, flags
        (mandatory, read only) and comment (if any) for each or selected
        entries.

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

    def inspect(self, file=None, issue_handling="print"):
        """
        Get information about data inside a SOFA object.

        Prints the values of all attributes and variables with six or less
        entries and the shapes and type of all numeric and string variables.
        When printing the values of arrays, single dimensions are discarded for
        easy of display, i.e., an array of shape (1, 3, 2) will be displayed as
        an array of shape (3, 2).

        Parameters
        ----------
        file : str
            Full path of a file under which the information is to be stored in
            plain text. The default ``None`` does only print the information.
        issue_handling : str, optional
            Defines how issues detected during verification of the SOFA object
            are handeled (see :py:func:`~sofar.sofar.Sofa.verify`)

            ``'raise'``
                Warnings and errors are raised if issues are detected
            ``'print'``
                Issues are printed without raising warnings and errors
            ``'return'``
                Issues are returned as string but neither raised nor printed
            ``'ignore'``
                Issues are ignored, i.e., not raised, printed, or returned.

            The default is ``print'``.
        """

        # update the private attribute `_convention` to make sure the required
        # meta data is in place
        self.verify(version="match", issue_handling=issue_handling)

        # list of all attributes
        keys = [k for k in self.__dict__.keys() if not k.startswith("_")]

        # start printing the information
        info_str = (
            f"{self.GLOBAL_SOFAConventions} "
            F"{self.GLOBAL_SOFAConventionsVersion} "
            f"(SOFA version {self.GLOBAL_Version})\n")
        info_str += "-" * len(info_str) + "\n"

        for key in keys:

            info_str += key + " : "
            value = getattr(self, key)

            # information for attributes and scalars
            if self._convention[key]["type"] == "attribute" or value.size == 1:
                info_str += str(value) + "\n"
            # information for variables
            else:
                # get shape and dimension
                shape = value.shape
                dimension = self._dimensions[key]

                # pad shape if required (trailing single dimensions are
                # discarded following the numpy default)
                while len(shape) < len(dimension):
                    shape += (1, )

                # make verbose shape, e.g., '(M=100, R=2, N=128, '
                shape_verbose = "("
                for s, d in zip(shape, dimension):
                    shape_verbose += f"{d}={s}, "

                # add shape information
                info_str += shape_verbose[:-2] + ")\n"
                # add value information if not too much
                if value.size < 7:
                    info_str += "  " + \
                        str(np.squeeze(value)).replace("\n", "\n  ") + "\n"

        # write to text file
        if file is not None:
            with open(file, 'w') as f_id:
                f_id.write(info_str + "\n")

        # output to console
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

    def delete(self, name):
        """
        Delete variable or attribute from SOFA object.

        Note that mandatory data can not be deleted. Call
        :py:func:`Sofa.info("optional") <sofar.sofar.Sofa.info>` to list all
        optional variables and attributes.

        Parameters
        ----------
        name : str
            Name of the variable or attribute to be deleted
        """
        delattr(self, name)

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
        self._add_custom_api_entry(name, value, None, dimensions, dtype)

    def _add_custom_api_entry(self, key, value, flags, dimensions, dtype):
        """
        Add custom entry to the sofa._convention and permanently save it in
        sofa._custom

        Parameters
        ----------
        key : str
            name of the entry
        value: any
            Value of the entry
        flags, dimensions, dtype : any
            as in sofa._convention
        dimensions : string
            Dimensions in case of numeric or string array
        dtype : string
            double, string, or attribute
        """
        # create custom API if it not exists
        self._protected = False
        if not hasattr(self, "_custom"):
            self._custom = {}

        # lower case letters to indicate custom dimensions
        if dimensions is not None:
            dimensions = [d.upper() if d.upper() in "ERMNCIS" else d.lower()
                          for d in dimensions]
            dimensions = "".join(dimensions)

        # add user entry to custom API
        self._custom[key] = {
            "flags": flags,
            "dimensions": dimensions,
            "type": dtype,
            "default": None,
            "comment": ""}
        self._update_convention(version="match")

        # add attribute to object
        setattr(self, key, value)
        self._protected = True

    def verify(self, version="latest", issue_handling="raise", mode="write"):
        """
        Verify a SOFA object against the SOFA standard.

        This function updates the API, and checks the following

        - Are all mandatory data contained? If `issue_handling` is ``"raise"``
          missing mandatory data raises an error. Otherwise mandatory data are
          added with their default value and a warning is given.
        - Are the names of variables and attributes in accordance to the SOFA
          standard?
        - Are the data types in accordance with the SOFA standard?
        - Are the dimensions of the variables consistent and in accordance
          to the SOFA standard?
        - Are the values of attributes consistent and in accordance to the
          SOFA standard?

        A detailed set of validation rules can be found at
        https://github.com/pyfar/sofar/tree/main/sofar/verification_rules

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
        mode : str, optional
            The SOFA standard is more strict for writing data than for reading
            data.

            ``'write'``
                All units (e.g. 'meter') must be written be lower case.
            ``'read'``
                Units can contain upper case letters (e.g. 'Meter')

            The default is ``'write'``

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
        missing = ""
        keys = [key for key in self.__dict__.keys() if not key.startswith("_")]

        for key in self._convention.keys():
            if self._mandatory(self._convention[key]["flags"]) \
                    and key not in keys:

                if issue_handling != "raise":
                    # add missing data with default value
                    self._protected = False
                    setattr(self, key, self._convention[key]["default"])
                    self._protected = True

                # prepare to raise warning
                missing += "- " + key + "\n"

        if missing:
            if issue_handling == "raise":
                error_msg += "Detected missing mandatory data:\n"
                error_msg += missing
            else:
                warning_msg += "Added mandatory data with default values:\n"
                warning_msg += missing

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
        if error_msg != "\nERRORS\n------\n" and issue_handling != "ignore":
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

        # check reserved names
        current_error = ""
        for key in keys:

            # AES69-2020 Sec. 4.7.1
            if key.startswith("PRIVATE") or key.startswith("API"):
                current_error += "- " + key + "\n"
            if (key.startswith("GLOBAL") and not key.startswith("GLOBAL_")) or\
                    (key.startswith("GLOBAL") and
                     self._convention[key]["type"] != "attribute"):
                current_error += "- " + key + "\n"

        if current_error:
            error_msg += (
                "Detected variable or attribute with reserved key words "
                "PRIVATE, API, or GLOBAL:\n")
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
        rules, unit_aliases = self._verification_rules()

        current_error = ""
        for key in rules.keys():

            # convert to sofar format
            key_sofar = key.replace(".", "_").replace(":", "_")

            if not hasattr(self, key_sofar):
                continue

            # actual and possible values for the current key
            test = getattr(self, key_sofar)
            ref = rules[key]["value"]

            # test if the value is valid
            if not self._verify_value(test, ref, unit_aliases, key_sofar):
                current_error += (f"- {key_sofar} is {test} "
                                  f"but must be {', '.join(ref)}\n")

            # get lower case value for of test for verifying specific
            # dependencies
            if isinstance(test, str) and test.lower() in \
                    ["cartesian", "spherical", "spherical harmonics"]:
                test = test.lower()

            # check general dependencies
            items = rules[key]["general"] if "general" in rules[key] else []

            for key_dep in items:

                # convert key to sofar format
                key_dep = key_dep.replace(".", "_").replace(":", "_")

                # check if dependency is contained in SOFA object hard to test,
                # for mandatory fields (added by sofar by default).
                if not hasattr(self, key_dep):
                    current_error += (f"- {key_dep} must be given if "
                                      f"{key_sofar} is in SOFA object\n")
                    continue

            # check specific dependencies
            if "specific" in rules[key] \
                    and test in rules[key]["specific"]:
                items = rules[key]["specific"][test].items()
            else:
                items = {}.items()

            for key_dep, ref_dep in items:

                if key_dep == "_dimensions":
                    # requires specific dimension(s) to have a vertain size
                    for dim in rules[key]["specific"][test]["_dimensions"]:
                        # possible sizes
                        dim_ref = \
                            rules[key]["specific"][test]["_dimensions"][dim]["value"]  # noqa
                        # current size
                        dim_act = self._api[dim]
                        # verbose error string for possible sizes
                        dim_str = \
                            rules[key]["specific"][test]["_dimensions"][dim]["value_str"]  # noqa
                        # perform the check
                        if dim_act not in dim_ref:
                            current_error += \
                                (f"- Dimension {dim} is of size {dim_act} "
                                 f"but must be {dim_str} if {key_sofar} "
                                 f"is {test}\n")
                else:

                    # convert name from NetCDF format to sofar format
                    key_dep_sofar = key_dep.replace(".", "_").replace(":", "_")

                    # check if dependency is contained in SOFA object
                    if not hasattr(self, key_dep_sofar):
                        current_error += (f"- {key_dep_sofar} must be given if"
                                          f" {key_sofar} is {test}\n")
                        continue

                    # check if dependency has the correct value
                    if ref_dep is None:
                        continue

                    # convert name from NetCDF format to sofar format
                    test_dep = getattr(self, key_dep_sofar)

                    if not self._verify_value(
                            test_dep, ref_dep, unit_aliases, key_dep_sofar):
                        current_error += (
                            f"- {key_dep_sofar} is {test_dep} but must be "
                            f"{', '.join(ref_dep)} if {key_sofar} is {test}\n")

        # ---------------------------------------------------------------------
        # 7. check write only restrictions: units shall be in lower-case
        # (could be tested in _verify_unit but this way a more verbose error
        # message can be generated)

        if mode == "write":
            keys = [k for k in self.__dict__.keys() if k.endswith("Units")]
            for key in keys:
                unit = getattr(self, key)
                if unit.lower() != unit:
                    current_error += (f"- {key} is {unit} but must contain "
                                      "only lower case letters when writing "
                                      "SOFA files to disk.")

        if current_error:
            error_msg += "Detected violations of the SOFA convention:\n"
            error_msg += current_error

        # ---------------------------------------------------------------------
        # 8. handle warnings and errors
        if issue_handling != "ignore":
            error_occurred, issues = self._verify_handle_issues(
                    warning_msg, error_msg, issue_handling)

            if error_occurred:
                if issue_handling == "print":
                    return
                elif issue_handling == "return":
                    return issues

    @staticmethod
    def _verify_value(test, ref, unit_aliases, key):
        """
        Check a value agains the SOFA standard for Sofa.verify()

        Parameters
        ----------
        test :
            the value under test
        ref :
            the value enforced by the SOFA standard
        unit_aliases :
            dict of aliases for units from _verification_rules()
        key :
            The name of the current attribute, e.g., "GLOBAL_DataType"

        Returns
        -------
        ``True`` if `test` and `ref` agree, ``False`` otherwise
        """

        # General case of valid value
        if ref is None or test in ref:
            return True

        # only string data should remain for verification
        if not isinstance(test, str):
            raise TypeError((
                "At this point, only string data should remain. Please report "
                "the issue: github.com/pyfar/sofar/issues"))

        # case sensitive check for DataType and SOFAConventions
        if key in ["GLOBAL_DataType", "GLOBAL_SOFAConventions"]:
            if test in ref:
                return True
            else:
                return False

        # general case insensitive test
        test = test.lower()
        if test in ref:
            return True

        # if we are not checking a unit, the test value is invalid
        if key.endswith("Units"):
            return sf.Sofa._verify_unit(test, ref, unit_aliases)
        else:
            return False

    @staticmethod
    def _verify_unit(test, ref, unit_aliases):
        """
        Verify if a unit string agrees with AES69

        Parameters:
        -----------
        test : string
            Current unit string (single units or multiple units separated by
            commas, commas plus spaces, or spaces).
        ref : list
            List of length one containing the LOWER reference case unit string,
            i.e., only the keys from unit_aliases are allowed words.
        unit_aliases : dict
            dict of aliases for units from _verification_rules()

        Returns
        -------
        verified : bool
        """
        # check format of reference units
        if not isinstance(ref, list) \
                or len(ref) != 1 \
                or not isinstance(ref[0], str):
            raise TypeError("ref must be a list of length 1 containing a str")

        # Following the SOFA standard AES69-2020, units may be separated by
        # `, ` (comma and space), `,` (comma only), and ` ` (space only).
        # (regexp ', ?' matches ', ' and ',')
        units_ref = re.split(', ?| ', ref[0])
        units_test = re.split(', ?| ', test)

        # check if number of units agree
        if len(units_ref) != len(units_test):
            return False

        # check if units are valid
        for unit_test, unit_ref in zip(units_test, units_ref):
            if unit_test not in unit_aliases \
                    or unit_aliases[unit_test] != unit_ref:
                return False

        # separate check for "cubic metre" (Since multi unit strings can be
        # separated by spaces, "cubic metre" is considered as such and is
        # split into a list ["cubic", "metre"])
        if "cubic" in units_test and (len(units_test) != 2 or
                                      unit_aliases[units_test[1]] != "metre"):
            return False

        return True

    @staticmethod
    def _get_reference_unit(test, unit_aliases):
        """
        Return units in reference for, .e.g.,
        "meter" is converted to "metre" and
        "degrees degrees,meter" is converted to "degree, degree, metre"

        Parameters:
        -----------
        test : string
            Current unit string MUST be valid, i.e., tested with
            Sofa._verify_unit (single units or multiple units separated by
            commas, commas plus spaces, or spaces).
        unit_aliases : dict
            dict of aliases for units from _verification_rules()

        Returns
        -------
        reference_units : str
        """
        # Following the SOFA standard AES69-2020, units may be separated by
        # `, ` (comma and space), `,` (comma only), and ` ` (space only).
        # (regexp ', ?' matches ', ' and ',')
        units_test = re.split(', ?| ', test.lower())

        # get list of reference units
        units = [unit_aliases[u] for u in units_test]
        # get reference unit string
        units = ", ".join(units) if units[0] != "cubic" else " ".join(units)

        return units

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

    @staticmethod
    def _verification_rules():
        """
        Return dictionaries to verify SOFA objects in Sofa.verify(). For
        detailed information see folder 'verification_rules'.

        Returns:
        data : dict
            General restrictions on the data of any SOFA convention
        data_type : dict
            Restriction depending on GLOBAL_DataType
        api : dict
            Restrictions on the API depending on specific fields of a SOFA file
        convention : dict
            Restrictions for specific conventions
        unit_aliases : dict
            Allowed aliases for the standard units
        """

        base = os.path.join(os.path.dirname(__file__), "verification_rules")

        with open(os.path.join(base, "rules.json"), "r") as file:
            rules = json.load(file)
        with open(os.path.join(base, "unit_aliases.json"), "r") as file:
            unit_aliases = json.load(file)

        return rules, unit_aliases

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

        # get available versions as strings
        versions = [p.split('_')[-1][:-5] for p in path]

        # select the correct version
        if version == "latest":
            versions = np.array([float(v) for v in versions])
            path = path[np.argmax(versions)]
        else:
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
