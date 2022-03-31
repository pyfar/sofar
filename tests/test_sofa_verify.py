"""Tests for sofar.Sofa.verify()"""
import sofar as sf
import pytest
from pytest import raises
import numpy as np


def test_version():
    """Test upgrading, downgrading, and keeping specific versions"""

    # test the default "latest"
    sofa = sf.Sofa("GeneralTF", version="1.0")
    assert str(sofa.GLOBAL_SOFAConventionsVersion) == "1.0"
    with pytest.warns(UserWarning, match="Upgraded"):
        sofa.verify()
    assert str(sofa.GLOBAL_SOFAConventionsVersion) == "2.0"

    # test "match"
    sofa = sf.Sofa("GeneralTF", version="1.0")
    assert str(sofa.GLOBAL_SOFAConventionsVersion) == "1.0"
    sofa.verify(version="match")
    assert str(sofa.GLOBAL_SOFAConventionsVersion) == "1.0"

    # test downgrading
    sofa = sf.Sofa("GeneralTF")
    assert str(sofa.GLOBAL_SOFAConventionsVersion) == "2.0"
    with pytest.warns(UserWarning, match="Downgraded"):
        sofa.verify(version="1.0")
    assert str(sofa.GLOBAL_SOFAConventionsVersion) == "1.0"


def test_missing_default_attributes(capfd):

    # test missing default attribute
    sofa = sf.Sofa("GeneralTF")
    sofa._protected = False
    delattr(sofa, "GLOBAL_Conventions")
    sofa._protected = True

    # raises error
    with raises(ValueError, match="Detected missing mandatory data"):
        sofa.verify(issue_handling="raise")

    # prints warning and adds data
    sofa.verify(issue_handling="print")
    out, _ = capfd.readouterr()

    assert "Added mandatory data with default values" in out
    assert sofa.GLOBAL_Conventions == "SOFA"


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
    with raises(ValueError, match="- Data_IR must be int, float"):
        sofa.verify()

    sofa.Data_IR = 1+1j
    with raises(ValueError, match="- Data_IR must be int, float"):
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


def test_wrong_shape():

    # test attribute with wrong shape
    sofa = sf.Sofa("GeneralTF")
    sofa.ListenerPosition = 1
    with raises(ValueError, match=("- ListenerPosition has shape")):
        sofa.verify()


def test_wrong_name():

    # attribute with missing variable
    sofa = sf.Sofa("GeneralTF")
    sofa._protected = False
    sofa.IR_Type = "pressure"
    sofa._custom = {"IR_Type": {"default": None,
                                "flags": None,
                                "dimensions": None,
                                "type": "attribute",
                                "comment": ""}}
    sofa._protected = True

    with raises(ValueError, match="Detected attributes with missing"):
        sofa.verify()

    # attribute with no underscore
    sofa = sf.Sofa("GeneralTF")
    sofa._protected = False
    sofa.IRType = "pressure"
    sofa._custom = {"IRType": {"default": None,
                               "flags": None,
                               "dimensions": None,
                               "type": "attribute",
                               "comment": ""}}
    sofa._protected = True

    with raises(ValueError, match="Detected attribute names with too many"):
        sofa.verify()

    # variable with underscore
    sofa = sf.Sofa("GeneralTF")
    sofa._protected = False
    sofa.IR_Data = 1
    sofa._custom = {"IR_Data": {"default": None,
                                "flags": None,
                                "dimensions": "IM",
                                "type": "double",
                                "comment": ""}}
    sofa._protected = True

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


# test everything from Sofa._verification_rules explicitly to make sure
# all possible error in SOFA files are caught
@pytest.mark.parametrize("key,value,msg", [
    ("GLOBAL_DataType", "image", "GLOBAL_DataType is image but must be FIR,"),
    ("GLOBAL_SOFAConventions", "FIR", ""),         # message tested above
    ("GLOBAL_RoomType", "Living room", ""),        # message tested above
    ("ListenerPosition_Type", "cylindrical", ""),  # message tested above
    ("ListenerPosition_Units", "A",
     "ListenerPosition_Units is A but must be metre if ListenerPosition_Type"),
    ("ListenerView_Type", "cylindrical", ""),      # message tested above
    ("ListenerView_Units", "A", ""),               # message tested above
    ("ReceiverPosition_Type", "cylindrical", ""),  # message tested above
    ("ReceiverPosition_Units", "A", ""),           # message tested above
    ("ReceiverView_Type", "cylindrical", ""),      # message tested above
    ("ReceiverView_Units", "A", ""),               # message tested above
    ("SourcePosition_Type", "cylindrical", ""),    # message tested above
    ("SourcePosition_Units", "A", ""),             # message tested above
    ("SourceView_Type", "cylindrical", ""),        # message tested above
    ("SourceView_Units", "A", ""),                 # message tested above
    ("EmitterPosition_Type", "cylindrical", ""),   # message tested above
    ("EmitterPosition_Units", "A", ""),            # message tested above
    ("EmitterView_Type", "cylindrical", ""),       # message tested above
    ("EmitterView_Units", "A", ""),                # message tested above
    ("RoomVolume_Units", "square metre", ""),      # message tested above
    ("RoomTemperature_Units", "Celsius", ""),      # message tested above
])
def test_restrictions_data_wrong_value(key, value, msg):
    """
    Test assertions for generally restricted data values.
    """

    sofa = sf.Sofa("SingleRoomSRIR")
    # add variables for testing certain dependencies. If cases in case the
    # variables get added to the convetion some time later.
    if not hasattr(sofa, "RoomVolume"):
        sofa.add_variable("RoomVolume", 200, "double", 'I')
        sofa.add_attribute("RoomVolume_Units", "cubic metre")
    if not hasattr(sofa, "RoomTemperature"):
        sofa.add_variable("RoomTemperature", 100, "double", 'I')
        sofa.add_attribute("RoomTemperature_Units", "kelvin")
    sofa._protected = False
    setattr(sofa, key, value)
    sofa._protected = True
    with raises(ValueError, match=msg):
        sofa.verify()


# can't test everything from Sofa._verification_rules explicitly because
# mandatory fields are added by default
@pytest.mark.parametrize("key,msg", [
    ("ReceiverView", "ReceiverView must be given if ReceiverUp"),
    ("RoomVolume_Units", ""),                      # message tested above
    ("RoomTemperature_Units", ""),                 # message tested above
])
def test_restrictions_data_missing_attribute(key, msg):
    """
    Test assertions for removing optional fields that become mandatory due to
    another field.
    """

    sofa = sf.Sofa("SingleRoomSRIR")
    # add variables for testing certain dependencies. If cases in case the
    # variables get added to the convnetion some time later.
    if not hasattr(sofa, "RoomVolume"):
        sofa.add_variable("RoomVolume", 200, "double", 'I')
        sofa.add_attribute("RoomVolume_Units", "cubic metre")
    if not hasattr(sofa, "RoomTemperature"):
        sofa.add_variable("RoomTemperature", 100, "double", 'I')
        sofa.add_attribute("RoomTemperature_Units", "Kelvin")
    sofa._protected = False
    delattr(sofa, key)
    sofa._protected = True
    with raises(ValueError, match=msg):
        sofa.verify()


# test everything from Sofa._verification_rules explicitly to make sure
# all possible error in SOFA files are caught
@pytest.mark.parametrize("convention,key,value,msg", [
    ("GeneralFIR", "Data_SamplingRate_Units", "hz",
     "Data_SamplingRate_Units is hz but must be hertz"),
    ("GeneralTF", "N_LongName", "f",
     "N_LongName is f but must be frequency"),
    ("GeneralTF", "N_Units", "hz",
     "N_Units is hz but must be hertz"),
])
def test_restrictions_data_type(convention, key, value, msg):
    """Test assertions for values that are restricted by GLOBAL_DataType."""

    sofa = sf.Sofa(convention)
    setattr(sofa, key, value)
    with raises(ValueError, match=msg):
        sofa.verify()


def test_restrictions_api_spherical_harmonics():
    """
    Test assertions for incorrect number of emitters/receiver in case of
    spherical harmonics coordinate systems
    """

    sofa = sf.Sofa("GeneralFIR-E")
    sofa.ReceiverPosition_Type = "spherical harmonics"
    sofa.ReceiverPosition_Units = "degree, degree, metre"
    sofa.Data_IR = np.zeros((1, 2, 1, 1))
    sofa.Data_Delay = np.zeros((1, 2, 1))
    with raises(ValueError, match="Dimension R is of size 2 but must be"):
        sofa.verify()

    sofa = sf.Sofa("GeneralFIR-E")
    sofa.EmitterPosition_Type = "spherical harmonics"
    sofa.EmitterPosition_Units = "degree, degree, metre"
    sofa.Data_IR = np.zeros((1, 1, 1, 2))
    sofa.Data_Delay = np.zeros((1, 1, 2))
    with raises(ValueError, match="Dimension E is of size 2 but must be"):
        sofa.verify()


def test_restrictions_api_second_order_sections():
    """
    Test assertions for incorrect number of N in case of
    SOS data type
    """

    sofa = sf.Sofa("SimpleFreeFieldHRSOS")
    sofa.Data_SOS = np.zeros((1, 2, 1))
    with raises(ValueError, match="Dimension N is of size 1 but must be"):
        sofa.verify()


@pytest.mark.parametrize('convention,kwargs,msg', [
    ("GeneralFIR", [("GLOBAL_DataType", "FIR-E")], "GLOBAL_DataType is FIR-E"),
    ("GeneralFIR-E", [("GLOBAL_DataType", "FIR")], "GLOBAL_DataType is FIR"),
    ("GeneralFIRE", [("GLOBAL_DataType", "FIR")], "GLOBAL_DataType is FIR"),
    ("GeneralTF", [("GLOBAL_DataType", "TF-E")], "GLOBAL_DataType is TF-E"),
    ("GeneralTF-E", [("GLOBAL_DataType", "TF")], "GLOBAL_DataType is TF"),

    ("SimpleFreeFieldHRIR", [("GLOBAL_DataType", "FIR-E")],
     "GLOBAL_DataType is FIR-E"),
    ("SimpleFreeFieldHRIR", [("GLOBAL_RoomType", "echoic")],
     "GLOBAL_RoomType is echoic"),
    ("SimpleFreeFieldHRIR", [("EmitterPosition", np.zeros((2, 3)))],
     "Dimension E is of size 2 but must be 1 if GLOBAL"),
    ("SimpleFreeFieldHRIR",
     [("EmitterPosition_Type", "spherical harmonics"),
      ("EmitterPosition_Units", "degree, degree, metre")],
     "EmitterPosition_Type is spherical harmonics"),

    ("SimpleFreeFieldHRTF", [("GLOBAL_DataType", "TF-E")],
     "GLOBAL_DataType is TF-E"),
    ("SimpleFreeFieldHRTF", [("GLOBAL_RoomType", "echoic")],
     "GLOBAL_RoomType is echoic"),
    ("SimpleFreeFieldHRTF", [("EmitterPosition", np.zeros((2, 3)))],
     "Dimension E is of size 2 but must be 1 if GLOBAL"),
    ("SimpleFreeFieldHRTF",
     [("EmitterPosition_Type", "spherical harmonics"),
      ("EmitterPosition_Units", "degree, degree, metre")],
     "EmitterPosition_Type is spherical harmonics"),

    # DataType for SimpleFreeFieldHRSOS can not be checked. It raises an error
    # beforehands
    ("SimpleFreeFieldHRSOS", [("GLOBAL_RoomType", "echoic")],
     "GLOBAL_RoomType is echoic"),
    ("SimpleFreeFieldHRSOS", [("EmitterPosition", np.zeros((2, 3)))],
     "Dimension E is of size 2 but must be 1 if GLOBAL"),
    ("SimpleFreeFieldHRSOS",
     [("EmitterPosition_Type", "spherical harmonics"),
      ("EmitterPosition_Units", "degree, degree, metre")],
     "EmitterPosition_Type is spherical harmonics"),

    # Can not be tested, because it is not yet defined
    # ("FreeFieldHRIR", [("GLOBAL_DataType", "FIR")],
    #  "GLOBAL_DataType is FIR"),
    ("FreeFieldHRTF", [("GLOBAL_DataType", "TF")],
     "GLOBAL_DataType is TF"),
    ("SimpleHeadphoneIR", [("GLOBAL_DataType", "FIR-E")],
     "GLOBAL_DataType is FIR-E"),
    ("SingleRoomSRIR", [("GLOBAL_DataType", "FIR-E")],
     "GLOBAL_DataType is FIR-E"),
    ("SingleRoomMIMOSRIR", [("GLOBAL_DataType", "FIR")],
     "GLOBAL_DataType is FIR"),
    ("FreeFieldDirectivityTF", [("GLOBAL_DataType", "TF-E")],
     "GLOBAL_DataType is TF-E"),
])
def test_restrictions_convention(convention, kwargs, msg):

    sofa = sf.Sofa(convention)
    sofa._protected = False
    for key_value in kwargs:
        setattr(sofa, key_value[0], key_value[1])
    with raises(ValueError, match=msg):
        sofa.verify()


def test_read_and_write_mode():

    # Unit with uppercase is ok when reading but not ok when writing
    sofa = sf.Sofa("SimpleFreeFieldHRIR")
    sofa.ListenerPosition_Units = "Meter"

    assert sofa.verify(mode="read", issue_handling="return") is None
    with raises(ValueError, match="lower case letters when writing"):
        sofa.verify(mode="write")


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
    assert sf.Sofa._verify_value("degrees,degrees meter",
                                 ["degree, degree, metre"],
                                 unit_aliases, "Some_Units")

    # simple fail: single unit
    assert not sf.Sofa._verify_value("centimeter", ["metre"],
                                     unit_aliases, "Some_Units")

    # complex fail: list of units
    assert not sf.Sofa._verify_value("rad, rad, metre",
                                     ["degree, degree, metre"],
                                     unit_aliases, "Some_Units")


def test_ignore(capfd):
    """Test the ignore option of Sofa.verify"""

    # test invalid data for netCDF attribute
    sofa = sf.Sofa("GeneralFIR")
    sofa.GLOBAL_Comment = [1, 2, 3]
    issues = sofa.verify(issue_handling="ignore")

    assert issues is None
    assert capfd.readouterr() == ("", "")


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

    # report warning
    issue_handling = "report"
    with pytest.warns(None) as warning:
        _, issues = sf.Sofa._verify_handle_issues(
            warning_msg + "warning", error_msg, issue_handling)
    assert "warning" in issues
    assert "ERROR" not in issues
    assert len(warning) == 0
    # report error
    _, issues = sf.Sofa._verify_handle_issues(
            warning_msg, error_msg + "error", issue_handling)
    assert "error" in issues
    assert "WARNING" not in issues


def test_case_insensitivity():
    """
    Reading applications shall ignore the case of
    - units and
    - types of coordinate systems
    """

    # data type (must be case sensitive) --------------------------------------
    sofa = sf.Sofa("SimpleFreeFieldHRIR")
    sofa._protected = False
    sofa.GLOBAL_DataType = "fir"
    sofa._protected = True
    with raises(ValueError, match="GLOBAL_DataType is fir"):
        sofa.verify()

    # room type ---------------------------------------------------------------
    sofa = sf.Sofa("FreeFieldHRIR")
    sofa.GLOBAL_RoomType = "Free field"
    assert sofa.verify(issue_handling="return") is None

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
