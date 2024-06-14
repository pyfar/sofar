"""Tests for sofar.Sofa.verify()"""
import sofar as sf
from sofar.utils import _complete_sofa
import os
from glob import glob
import pytest
from pytest import raises
import numpy as np
import warnings

# get verification rules
_, unit_aliases, _, _ = sf.Sofa._verification_rules()

# directory containing the verificatin data
basedir = os.path.join(os.path.dirname(__file__), "..", "sofar",
                       "sofa_conventions", "data")

# files for testing the verification rules
restricted_values = glob(
    os.path.join(basedir, "restricted_values", "*.sofa"))
general_dependencies = glob(
    os.path.join(basedir, "general_dependencies", "*.sofa"))
specific_dependencies = glob(
    os.path.join(basedir, "specific_dependencies", "*.sofa"))
deprecations = glob(
    os.path.join(basedir, "deprecations", "*.sofa"))
restricted_dimensions = glob(
    os.path.join(basedir, "restricted_dimensions", "*.sofa"))


# general tests ---------------------------------------------------------------
def test_verify_value():
    # example alias for testing as returned by Sofa._verification_rules()
    unit_aliases = {"meter": "metre",
                    "degrees": "degree"}

    # Simple pass: no restriction on value
    assert sf.Sofa._verify_value("goofy", None, unit_aliases, "Some_Units")

    # simple pass: single unit
    assert sf.Sofa._verify_value(
        "meter", ["metre"], unit_aliases, "Some_Units")

    # complex pass: list of units
    assert sf.Sofa._verify_value("degrees, degrees, meter",
                                 ["degree, degree, metre"],
                                 unit_aliases, "Some_Units")

    # complex pass: list of units with other separators allowed by AES69
    assert sf.Sofa._verify_value("degrees,degrees, meter",
                                 ["degree, degree, metre"],
                                 unit_aliases, "Some_Units")

    # simple fail: single unit
    assert not sf.Sofa._verify_value("centimeter", ["metre"],
                                     unit_aliases, "Some_Units")

    # complex fail: list of units
    assert not sf.Sofa._verify_value("rad, rad, metre",
                                     ["degree, degree, metre"],
                                     unit_aliases, "Some_Units")


def test_issue_handling(capfd):
    """Test different methods for handling issues during verification"""

    error_msg = "\nERRORS\n------\n"
    warning_msg = "\nWARNINGS\n--------\n"

    # no issue
    issue_handling = "raise"
    error_occurred, issues = sf.Sofa._verify_handle_issues(
        warning_msg, error_msg, issue_handling)
    assert not error_occurred
    assert issues is None

    # raise
    issue_handling = "raise"
    with pytest.warns(UserWarning, match="warning"):
        sf.Sofa._verify_handle_issues(
            warning_msg + "warning", error_msg, issue_handling)
    with raises(ValueError, match="error"):
        sf.Sofa._verify_handle_issues(
            warning_msg, error_msg + "error", issue_handling)

    # print warning
    issue_handling = "print"
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        _, issues = sf.Sofa._verify_handle_issues(
            warning_msg + "warning", error_msg, issue_handling)
    out, _ = capfd.readouterr()
    assert "warning" in issues
    assert 'warning' in out
    assert "ERROR" not in issues
    assert "ERROR" not in out
    # print error
    _, issues = sf.Sofa._verify_handle_issues(
            warning_msg, error_msg + "error", issue_handling)
    out, _ = capfd.readouterr()
    assert "error" in issues
    assert 'error' in out
    assert "WARNING" not in issues
    assert "WARNING" not in out

    # test invalid data for netCDF attribute
    issue_handling = "ignore"
    sofa = sf.Sofa("GeneralFIR")
    sofa.GLOBAL_Comment = [1, 2, 3]
    issues = sofa.verify(issue_handling=issue_handling)

    assert issues is None
    assert capfd.readouterr() == ("", "")


def test_case_insensitivity():
    """
    Reading applications shall ignore the case of
    - units and
    - types of coordinate systems
    """

    # data type (must be case sensitive) --------------------------------------
    sofa = sf.Sofa("SimpleFreeFieldHRIR")
    sofa.protected = False
    sofa.GLOBAL_DataType = "fir"
    sofa.protected = True
    with raises(ValueError, match="GLOBAL_DataType is fir"):
        sofa.verify()

    # room type ---------------------------------------------------------------
    sofa = sf.Sofa("FreeFieldHRIR")
    sofa.GLOBAL_RoomType = "Free field"
    assert sofa.verify() is None

    # units -------------------------------------------------------------------
    # example alias for testing as returned by Sofa._verification_rules()
    unit_aliases = {"meter": "metre",
                    "degrees": "degree"}

    # case insensitive testing
    assert sf.Sofa._verify_value(
        "Meter", ["meter"], unit_aliases, "Some_Units")
    assert sf.Sofa._verify_value("DegrEes, dEgreeS, MeTer",
                                 ["degree, degree, metre"],
                                 unit_aliases, "Some_Units")

    sofa = sf.Sofa("FreeFieldDirectivityTF")
    sofa.N_Units = "HertZ"
    assert sofa.verify(issue_handling="return", mode="read") is None

    # coordinate types --------------------------------------------------------
    sofa = sf.Sofa("SimpleFreeFieldHRIR")
    sofa.ListenerPosition_Type = "Cartesian"
    assert sofa.verify(issue_handling="return") is None


# 1. check if the mandatory attributes are contained --------------------------
def test_missing_default_attributes(capfd):

    # test missing default attribute
    sofa = sf.Sofa("GeneralTF")
    sofa.protected = False
    delattr(sofa, "GLOBAL_Conventions")
    sofa.protected = True

    # raises error
    with raises(ValueError, match="Detected missing mandatory data"):
        sofa.verify(issue_handling="raise")

    # prints warning and adds data
    sofa.verify(issue_handling="print")
    out, _ = capfd.readouterr()

    assert "Added mandatory data with default values" in out
    assert sofa.GLOBAL_Conventions == "SOFA"


# 2. verify data type ---------------------------------------------------------
def test_data_types(capfd):

    # test invalid data for netCDF attribute
    sofa = sf.Sofa("GeneralFIR")
    sofa.GLOBAL_Comment = [1, 2, 3]
    with raises(ValueError, match="- GLOBAL_Comment must be string"):
        sofa.verify()

    # test invalid data for netCDF double variable
    sofa = sf.Sofa("GeneralFIR")
    sofa.Data_IR = np.array("test")
    with raises(ValueError, match="- Data_IR must be int or float"):
        sofa.verify()

    sofa.Data_IR = "1"
    with raises(ValueError, match="- Data_IR must be int or float"):
        sofa.verify()

    sofa.Data_IR = 1+1j
    with raises(ValueError, match="- Data_IR must be int or float"):
        sofa.verify()

    # test invalid data with issue_handling "print" and "return"
    sofa = sf.Sofa("GeneralFIR")
    sofa.Data_IR = np.array("test")
    out, _ = capfd.readouterr()
    issues = sofa.verify(issue_handling="print")
    out, _ = capfd.readouterr()
    assert issues is None
    assert "- Data_IR must be int or float" in out

    issues = sofa.verify(issue_handling="return")
    out, _ = capfd.readouterr()
    assert "- Data_IR must be int or float" in issues
    assert "- Data_IR must be int or float" not in out

    # test valid data
    sofa.Data_IR = np.array([1])
    sofa.verify()
    sofa.Data_IR = [1]
    sofa.verify()
    sofa.Data_IR = 1
    sofa.verify()

    # test invalid data for netCDF attribute
    sofa = sf.Sofa("GeneralFIR")
    sofa.GLOBAL_History = 1
    with raises(ValueError, match="- GLOBAL_History must be string"):
        sofa.verify()

    # test invalid data for netCDF string variable
    sofa = sf.Sofa("SimpleHeadphoneIR")
    sofa.SourceModel = 1
    with raises(ValueError, match="- SourceModel must be string"):
        sofa.verify()

    sofa.SourceModel = np.array(1)
    with raises(ValueError, match="- SourceModel must be U or S"):
        sofa.verify()

    # test valid data
    sofa.SourceModel = ["test"]
    sofa.verify()
    sofa.SourceModel = np.array(["test"])
    sofa.verify()


# 3. Verify names of entries --------------------------------------------------
def test_wrong_name():

    # attribute with missing variable
    sofa = sf.Sofa("GeneralTF")
    sofa.protected = False
    sofa.IR_Type = "pressure"
    sofa._custom = {"IR_Type": {"default": None,
                                "flags": None,
                                "dimensions": None,
                                "type": "attribute",
                                "comment": ""}}
    sofa.protected = True

    with raises(ValueError, match="Detected attributes with missing"):
        sofa.verify()

    # attribute with no underscore
    sofa = sf.Sofa("GeneralTF")
    sofa.protected = False
    sofa.IRType = "pressure"
    sofa._custom = {"IRType": {"default": None,
                               "flags": None,
                               "dimensions": None,
                               "type": "attribute",
                               "comment": ""}}
    sofa.protected = True

    with raises(ValueError, match="Detected attribute names with too many"):
        sofa.verify()

    # variable with underscore
    sofa = sf.Sofa("GeneralTF")
    sofa.protected = False
    sofa.IR_Data = 1
    sofa._custom = {"IR_Data": {"default": None,
                                "flags": None,
                                "dimensions": "IM",
                                "type": "double",
                                "comment": ""}}
    sofa.protected = True

    with raises(ValueError, match="Detected variable names with too many"):
        sofa.verify()

    # variables with reserved names
    sofa = sf.Sofa("GeneralTF")
    sofa.add_variable("APIfunk", 1, "double", "I")
    with raises(ValueError, match="with reserved key words"):
        sofa.verify()

    sofa = sf.Sofa("GeneralTF")
    sofa.add_variable("PRIVATEtreasure", 1, "double", "I")
    with raises(ValueError, match="with reserved key words"):
        sofa.verify()

    sofa = sf.Sofa("GeneralTF")
    sofa.add_variable("GLOBALdata", 1, "double", "I")
    with raises(ValueError, match="with reserved key words"):
        sofa.verify()


def test_custom_data_name():
    """
    Custom entries can not have the names of data contained in the convention.
    """

    sofa = sf.Sofa("GeneralTF")
    # add variable Origin, although GLOBAL_Origin exists
    sofa.add_variable("Origin", 1, "double", 'I')
    with raises(ValueError,
                match="custom variable or attribute with reserved names"):
        sofa.verify()


# 4 + 5. get and verify dimensions of data ------------------------------------
def test_wrong_shape():

    # test attribute with wrong shape
    sofa = sf.Sofa("GeneralTF")
    sofa.ListenerPosition = 1
    with raises(ValueError, match=("- ListenerPosition has shape")):
        sofa.verify()


# 6. check restrictions on the content of SOFA files --------------------------
def test_rules_error_messages():
    """
    Test the exact error messages raised by violated rules from rules.json. The
    remaining test check only if errors are raised.
    """

    # wrong value
    sofa = _complete_sofa()
    sofa.GLOBAL_RoomType = "pentagon"
    error = "GLOBAL_RoomType is pentagon but must be free field, reverberant"
    with raises(ValueError, match=error):
        sofa.verify()

    # missing general dependency
    sofa = _complete_sofa()
    sofa.delete("ListenerView_Type")
    error = "ListenerView_Type must be given if ListenerView is in SOFA object"
    with raises(ValueError, match=error):
        sofa.verify()

    # wrong dimensions
    sofa = sf.Sofa("SimpleFreeFieldHRSOS")
    sofa.Data_SOS = np.zeros((1, 2, 1))
    error = ("Dimension N is of size 1 but must be an integer multiple of 6 "
             "greater 0 if GLOBAL_DataType is SOS")
    with raises(ValueError, match=error):
        sofa.verify()

    # missing specific dependency
    sofa = _complete_sofa()
    sofa.GLOBAL_RoomType = "reverberant"
    sofa.delete("GLOBAL_RoomDescription")
    error = ("GLOBAL_RoomDescription must be given "
             "if GLOBAL_RoomType is reverberant")
    with raises(ValueError, match=error):
        sofa.verify()

    # wrong value for specific dependency
    sofa = _complete_sofa()
    sofa.ListenerPosition_Type = "spherical"
    error = ("ListenerPosition_Units is metre but must be degree, degree, "
             "metre if ListenerPositionType is spherical")


@pytest.mark.parametrize("file", restricted_values)
def test_restricted_values(file):
    """Test all rules that restrict data to certain values"""

    try:
        # load file without verification
        sofa = sf.read_sofa(file, verify=False)
        # test verification
        with raises(ValueError, match="invalid-value"):
            sofa.verify()
    except ValueError as VE:
        assert str(VE) == "Convention 'invalid-value' does not exist"


@pytest.mark.parametrize("file", general_dependencies)
def test_general_dependencies(file):
    """Test all rules that restrict data to certain values"""

    # load file without verification
    sofa = sf.read_sofa(file, verify=False)

    # test verification
    with raises(ValueError, match="missing|must be given"):
        sofa.verify()


@pytest.mark.parametrize("file", specific_dependencies)
def test_specific_dependencies(file):

    # load file without verification
    sofa = sf.read_sofa(file, verify=False)

    # extract match for error message ('invalid-value' or 'missing')
    match = file[file.rfind("=")+1:file.rfind(".")]

    if match == "missing":
        match += "|must be given"

    with raises(ValueError, match=match):
        sofa.verify()


@pytest.mark.parametrize("file", restricted_dimensions)
def test_restricted_dimensions(file):

    # load file without verification
    sofa = sf.read_sofa(file, verify=False)

    # extract data for error message from filename
    match = f"Dimension {file[-8]} is of size {file[-6]} but must be"

    # test verification
    with raises(ValueError, match=match):
        sofa.verify()


# 7. check write only restrictions --------------------------------------------
def test_read_and_write_mode():

    # Unit with uppercase is ok when reading but not ok when writing
    sofa = sf.Sofa("SimpleFreeFieldHRIR")
    sofa.ListenerPosition_Units = "Meter"

    assert sofa.verify(mode="read", issue_handling="return") is None
    with raises(ValueError, match="lower case letters when writing"):
        sofa.verify(mode="write")


# 8. check deprecations -------------------------------------------------------
@pytest.mark.parametrize("file", deprecations)
def test_deprecations(file):
    """
    Test if deprecations raise warnings in read mode and errors in write mode.
    """

    # read file without verification
    sofa = sf.read_sofa(file, verify=False)

    # check if deprecated and substitute convention exist in sofar
    conventions = sf.utils._get_conventions("name")
    deprecated = sofa.GLOBAL_SOFAConventions

    if deprecated not in conventions:
        return

    # check warnings and errors
    sofa = sf.Sofa(deprecated, verify=False)

    msg = ("Detected deprecations:\n"
           f"- GLOBAL_SOFAConventions is {deprecated}, which is deprecated. ")

    with pytest.warns(UserWarning, match=msg):
        sofa.verify(mode="read")

    with raises(ValueError, match=msg):
        sofa.verify(mode="write")


def test_preliminary_conventions_version():
    """Test if using a convention version < 1.0 issues a warning"""

    with pytest.warns(UserWarning, match="Detected preliminary"):
        sf.Sofa("SingleRoomDRIR", version="0.3")
