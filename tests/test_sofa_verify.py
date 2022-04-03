"""Tests for sofar.Sofa.verify()"""
import sofar as sf
import pytest
from pytest import raises
import numpy as np

rules, unit_aliases, _ = sf.Sofa._verification_rules()


def complete_sofa(convention="GeneralTF"):
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
    sofa._protected = False
    sofa.GLOBAL_DataType = "fir"
    sofa._protected = True
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


# 0. update conventions -------------------------------------------------------
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


# 1. check if the mandatory attributes are contained --------------------------
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


# 3. Verify names of entries --------------------------------------------------
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
    sofa = complete_sofa()
    sofa.GLOBAL_RoomType = "pentagon"
    error = "GLOBAL_RoomType is pentagon but must be free field, reverberant"
    with raises(ValueError, match=error):
        sofa.verify()

    # missing general dependency
    sofa = complete_sofa()
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
    sofa = complete_sofa()
    sofa.GLOBAL_RoomType = "reverberant"
    sofa.delete("GLOBAL_RoomDescription")
    error = ("GLOBAL_RoomDescription must be given "
             "if GLOBAL_RoomType is reverberant")
    with raises(ValueError, match=error):
        sofa.verify()

    # wrong value for specific dependency
    sofa = complete_sofa()
    sofa.ListenerPosition_Type = "spherical"
    error = ("ListenerPosition_Units is metre but must be degree, degree, "
             "metre if ListenerPositionType is spherical")


def test_rules_values():
    """Test all rules that restrict data to certain values"""

    # key: name of variable or attribute for testing the rule
    for key in rules:
        if "value" not in rules[key]:
            continue

        key_sf = key.replace(".", "_").replace(":", "_")
        print(f"Testing: {key_sf}")
        sofa = complete_sofa()

        # test invalid value
        sofa._protected = False
        setattr(sofa, key_sf, "wurst")
        sofa._protected = True

        with raises(ValueError):
            sofa.verify()


def test_rules_general():
    """Test all rules that restrict data to certain values"""

    # key: name of variable or attribute for testing the rule
    for key in rules:
        if "general" not in rules[key]:
            continue

        for sub in rules[key]["general"]:

            sub_sf = sub.replace(".", "_").replace(":", "_")

            sofa = complete_sofa()
            sofa.delete(sub_sf)
            with raises(ValueError):
                sofa.verify()


def test_rules_specific():
    """
    Test all specific rules except for GLOBAL:DataType and
    GLOBAL:SOFAConventions, and restrictions on dimensions (tested below).
    Specific rules require certain variables or attributes to exist depending
    on a parent variable or attribute and sometines also restrict the value for
    the child.
    """
    keys = [k for k in rules.keys() if "specific" in rules[k] and k not in
            ["GLOBAL:DataType", "GLOBAL:SOFAConventions"]]

    # key: name of variable or attribute for testing specific dependency
    for key in keys:
        key_sf = key.replace(".", "_").replace(":", "_")

        # key_value: value of the variable or attribute that triggers the
        # specific dependency
        for value_key in rules[key]["specific"]:

            # sub: name of variable or attribute for which a specific
            # dependency is checked
            for sub in rules[key]["specific"][value_key]:

                if sub.startswith("_"):
                    continue

                sub_sf = sub.replace(".", "_").replace(":", "_")
                print(f"testing: {key}={value_key}, dependency {sub}")
                sofa = complete_sofa()

                # set key to correct value
                sofa._protected = False
                setattr(sofa, key_sf, value_key)
                sofa._protected = False

                # test a wrong value sor sub
                value_sub = rules[key]["specific"][value_key][sub]
                if value_sub is not None:
                    setattr(sofa, sub_sf, "wurst")
                    with raises(ValueError, match=f"{sub_sf} is wurst"):
                        sofa.verify()

                # test deleting sub
                sofa._protected = False
                delattr(sofa, sub_sf)
                sofa._protected = True
                with raises(ValueError):
                    sofa.verify()


def test_specific_rules_global_data_type():
    """Test all specific rules for GLOBAL_DataType"""

    for data_type in rules["GLOBAL:DataType"]["specific"]:

        if data_type in ["FIR", "FIR-E", "FIRE", "TF", "TF-E"]:
            convention = "General" + data_type
        elif data_type == "SOS":
            convention = "SimpleFreeFieldHRSOS"
        elif data_type == "FIRE":
            convention = "MultiSpeakerBRIR"

        for key in rules["GLOBAL:DataType"]["specific"][data_type]:
            if key.startswith("_"):
                continue

            key_sf = key.replace(".", "_").replace(":", "_")
            print(f"Testing: {data_type}, {key}")
            sofa = sf.Sofa(convention)

            # test a wrong value
            value = rules["GLOBAL:DataType"]["specific"][data_type][key]
            if value is not None:
                setattr(sofa, key_sf, "wurst")
                with raises(ValueError, match=f"{key_sf} is wurst"):
                    sofa.verify()

            # test deleting the attribute
            sofa._protected = False
            delattr(sofa, key_sf)
            sofa._protected = True
            with raises(ValueError, match="missing"):
                sofa.verify()


def test_specific_rules_convention():

    for convention in rules["GLOBAL:SOFAConventions"]["specific"]:
        for key in rules["GLOBAL:SOFAConventions"]["specific"][convention]:
            if key.startswith("_"):
                continue

            key_sf = key.replace(".", "_").replace(":", "_")
            print(f"Testing: {convention}, {key_sf}")
            sofa = sf.Sofa(convention)

            # test a wrong value
            sofa._protected = False
            setattr(sofa, key_sf, "wurst")
            sofa._protected = True

            with raises(ValueError, match=f"{key_sf} is wurst"):
                sofa.verify()

            # test deleting the attribute
            sofa._protected = False
            delattr(sofa, key_sf)
            sofa._protected = True
            with raises(ValueError, match="missing"):
                sofa.verify()


def test_specific_rules_dimensions():

    # test dimensions for spherical harmonics coordinates
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

    # test dimensions for SOS data type
    sofa = sf.Sofa("SimpleFreeFieldHRSOS")
    sofa.Data_SOS = np.zeros((1, 2, 1))
    with raises(ValueError, match="Dimension N is of size 1 but must be"):
        sofa.verify()

    # test dimensions for SimpleFreeFieldHRIR
    for convention in ["SimpleFreeFieldHRIR",
                       "SimpleFreeFieldHRTF",
                       "SimpleFreeFieldHRSOS"]:
        sofa = sf.Sofa(convention)
        sofa.EmitterPosition = [[1, 0, 0], [0, 1, 0]]
        with raises(ValueError, match="Dimension E is of size 2 but must be"):
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
# so far there only deprections on the Convention, and not all deprecated
# conventions still exist in API_MO. Thus the manual test intead of iterating
# over deprecations.json
@pytest.mark.parametrize("deprecated,current", (
    ["SingleRoomDRIR", "SingleRoomSRIR"],
    ["SimpleFreeFieldSOS", "SimpleFreeFieldHRSOS"]))
def test_deprecations(deprecated, current):
    sofa = sf.Sofa(deprecated, verify=False)

    msg = ("Detected deprecations:\n"
           f"- GLOBAL_SOFAConventions is {deprecated}, which is deprecated. "
           f"Use {current} instead.")

    with pytest.warns(UserWarning, match=msg):
        sofa.verify(mode="read")

    with raises(ValueError, match=msg):
        sofa.verify(mode="write")
