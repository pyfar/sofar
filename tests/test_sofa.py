"""Tests for sofar.Sofa (test for Sofa.verifycontained in test_sofa_verify)"""
import sofar as sf
import os
from tempfile import TemporaryDirectory
import pytest
from pytest import raises
import numpy as np


def test_create_sofa_object(capfd):
    # test assertion for type of convention parameter
    with raises(TypeError, match="Convention must be a string"):
        sf.Sofa(1)
    # test assertion for invalid conventions
    with raises(ValueError, match="Convention 'invalid' not found"):
        sf.Sofa("invalid")

    # test creation with defaults
    sofa = sf.Sofa("GeneralTF")
    assert isinstance(sofa, sf.Sofa)
    assert sofa.GLOBAL_SOFAConventionsVersion == "2.0"
    assert hasattr(sofa, '_convention')
    assert hasattr(sofa, '_dimensions')
    assert hasattr(sofa, '_api')

    # assert __repr__
    print(sofa)
    out, _ = capfd.readouterr()
    assert out == "sofar.SOFA object: GeneralTF 2.0\n"

    # test returning only mandatory fields
    sofa_all = sf.Sofa("GeneralTF")
    sofa_man = sf.Sofa("GeneralTF", mandatory=True)
    assert len(sofa_all.__dict__) > len(sofa_man.__dict__)

    # test version parameter
    sofa = sf.Sofa("GeneralTF", version="1.0")
    assert str(sofa.GLOBAL_SOFAConventionsVersion) == "1.0"

    # test invalid version
    with raises(ValueError, match="Version 0.25 not found. Available"):
        sf.Sofa("GeneralTF", version="0.25")

    # test without updating the api
    sofa = sf.Sofa("GeneralTF", verify=False)
    assert hasattr(sofa, '_convention')
    assert not hasattr(sofa, '_dimensions')
    assert not hasattr(sofa, '_api')


def test_set_attributes_of_sofa_object():
    sofa = sf.Sofa("GeneralTF")

    # set attribute
    assert (sofa.ListenerPosition == [0, 0, 0]).all()
    sofa.ListenerPosition = np.array([1, 1, 1])
    assert (sofa.ListenerPosition == [1, 1, 1]).all()

    # set read only attribute
    with raises(TypeError, match="GLOBAL_Version is a read only"):
        sofa.GLOBAL_Version = 1

    # set non-existing attribute
    with raises(TypeError, match="new is an invalid attribute"):
        sofa.new = 1


def test_delete_attribute_from_sofa_object():
    sofa = sf.Sofa("GeneralTF")

    # delete optional attribute
    delattr(sofa, "GLOBAL_ApplicationName")

    # delete mandatory attribute
    with raises(TypeError, match="GLOBAL_Version is a mandatory"):
        delattr(sofa, "GLOBAL_Version")

    # delete not existing attribute
    with raises(TypeError, match="new is not an attribute"):
        delattr(sofa, "new")


def test_copy_sofa_object():
    sofa_org = sf.Sofa("GeneralTF")
    sofa_cp = sofa_org.copy()

    assert sf.equals(sofa_org, sofa_cp, verbose=False)
    assert id(sofa_org) != id(sofa_cp)


def test_list_dimensions(capfd):

    # test FIR Data
    sofa = sf.Sofa("GeneralFIR")
    sofa.list_dimensions
    out, _ = capfd.readouterr()
    assert "N = 1 samples (set by Data_IR of dimension MRN)" in out

    # test TF Data
    sofa = sf.Sofa("GeneralTF")
    sofa.list_dimensions
    out, _ = capfd.readouterr()
    assert "N = 1 frequencies (set by Data_Real of dimension MRN)" in out

    # test SOS Data
    sofa = sf.Sofa("SimpleFreeFieldHRSOS")
    sofa.list_dimensions
    out, _ = capfd.readouterr()
    assert "N = 6 SOS coefficients (set by Data_SOS of dimension MRN)" in out

    # test non spherical harmonics data
    sofa = sf.Sofa("GeneralFIR")
    sofa.list_dimensions
    out, _ = capfd.readouterr()
    assert "E = 1 emitter" in out
    assert "R = 1 receiver" in out

    sofa.EmitterPosition_Type = "spherical harmonics"
    sofa.ReceiverPosition_Type = "spherical harmonics"
    sofa.EmitterPosition_Units = "degree, degree, metre"
    sofa.ReceiverPosition_Units = "degree, degree, metre"
    sofa.list_dimensions
    out, _ = capfd.readouterr()
    assert "E = 1 emitter spherical harmonics coefficients" in out
    assert "R = 1 receiver spherical harmonics coefficients" in out

    # test assertion in case of variables with wrong type or shape
    sofa = sf.Sofa("GeneralFIR")
    sofa.Data_IR = "test"
    with raises(ValueError, match="Dimensions can not be shown"):
        sofa.list_dimensions
    sofa.Data_IR = [1, 2, 3, 4]
    with raises(ValueError, match="Dimensions can not be shown"):
        sofa.list_dimensions


def test_get_dimension():
    """Test getting the size of dimensions"""

    # test FIR Data
    sofa = sf.Sofa("GeneralFIR")
    size = sofa.get_dimension("N")
    assert size == 1

    # test with wrong dimension
    with raises(ValueError, match="Q is not a valid dimension"):
        size = sofa.get_dimension("Q")


def test_info(capfd):

    sofa = sf.Sofa("SimpleFreeFieldHRIR")

    # test with wrong info string
    with raises(
            ValueError, match="info='invalid' is invalid"):
        sofa.info("invalid")

    # test with default parameter
    sofa.info()
    out, _ = capfd.readouterr()
    assert "showing all entries" in out

    # test listing all entry names
    for info in ["all", "mandatory", "optional", "read only", "data"]:
        sofa.info(info)
        out, _ = capfd.readouterr()
        assert f"showing {info} entries" in out

    # list information for specific entry
    sofa.info("ListenerPosition")
    out, _ = capfd.readouterr()
    assert "ListenerPosition\n    type: double" in out
    assert "ListenerPosition_Type\n    type: attribute" in out
    assert "ListenerPosition_Units\n    type: attribute" in out


def test_inspect(capfd):

    temp_dir = TemporaryDirectory()
    file = os.path.join(temp_dir.name, "info.txt")

    sofa = sf.Sofa("SimpleFreeFieldHRIR")

    # inspect file
    sofa.inspect(file)

    # check terminal output
    out, _ = capfd.readouterr()
    assert "GLOBAL_SOFAConventions : SimpleFreeFieldHRIR" in out
    assert ("ReceiverPosition : (R=2, C=3, I=1)\n"
            "  [[ 0.    0.09  0.  ]\n"
            "   [ 0.   -0.09  0.  ]]") in out

    # check text file
    with open(file, "r") as f_id:
        text = f_id.readlines()
    assert out == "".join(text)


def test_add_entry():

    sofa = sf.Sofa("GeneralTF")

    tmp_dir = TemporaryDirectory()

    # test adding a single variable entry
    sofa.add_variable("Temperature", 25.1, "double", "MI")
    entry = {"flags": None, "dimensions": "MI", "type": "double",
             "default": None, "comment": ""}
    assert sofa.Temperature == 25.1
    assert sofa._custom["Temperature"] == entry
    assert sofa._convention["Temperature"] == entry

    # test adding string variable, global and local attributes
    sofa.add_variable("Mood", "good", "string", "MS")
    assert sofa.Mood == "good"
    sofa.add_attribute("GLOBAL_Mood", "good")
    assert sofa.GLOBAL_Mood == "good"
    sofa.add_attribute("Temperature_Units", "degree celsius")
    assert sofa.Temperature_Units == "degree celsius"

    # check if everything can be verified and written, and read correctly
    sf.write_sofa(os.path.join(tmp_dir.name, "tmp.sofa"), sofa)
    sofa_read = sf.read_sofa(os.path.join(tmp_dir.name, "tmp.sofa"))
    assert sf.equals(sofa, sofa_read)

    # test deleting an entry
    delattr(sofa, "Temperature_Units")
    assert not hasattr(sofa, "Temperature_Units")
    assert "Temperature_Units" not in sofa._custom

    # test adding missing entry defined in convention
    sofa.protected = False
    delattr(sofa, "ListenerPosition")
    sofa.protected = True
    sofa.add_variable("ListenerPosition", [0, 0, 0], "double", "IC")
    assert "ListenerPosition" not in sofa._custom

    # test assertions
    # add existing entry
    with raises(ValueError, match="Entry Temperature already exists"):
        sofa.add_variable("Temperature", 25.1, "double", "MI")
    # entry violating the naming convention
    with raises(ValueError, match="underscores '_' in the name"):
        sofa.add_variable("Temperature_Celsius", 25.1, "double", "MI")
    with raises(ValueError, match="The name of Data"):
        sofa.add_attribute("Data_Time_measured", "midnight")
    # entry with wrong type
    with raises(ValueError, match="dtype is float but must be"):
        sofa.add_variable("TemperatureCelsius", 25.1, "float", "MI")
    # variable without dimensions
    with raises(ValueError, match="dimensions must be provided"):
        sofa.add_variable("TemperatureCelsius", 25.1, "double", None)
    # invalid dimensins
    with pytest.warns(UserWarning, match="Added custom dimension T"):
        sofa.add_variable("TemperatureCelsius", [25.1, 25.2], "double", "T")
    # attribute with missing variable
    with raises(ValueError, match="Adding Attribute Variable"):
        sofa.add_attribute("Variable_Unit", "celsius")


@pytest.mark.parametrize("mandatory,optional",
                         [(True, False), (False, True), [True, True]])
@pytest.mark.parametrize("verbose", [True, False])
def test_add_missing(
        mandatory, optional, verbose, capfd):

    sofa = sf.Sofa("GeneralTF")

    # attributes for testing
    man = "GLOBAL_AuthorContact"
    opt = "GLOBAL_History"

    # remove data before adding it again
    sofa.protected = False
    sofa.delete(man)
    sofa.delete(opt)
    sofa.protected = False

    # add missing data
    sofa.add_missing(mandatory, optional, verbose)
    out, _ = capfd.readouterr()

    if mandatory and optional:
        assert hasattr(sofa, man) and hasattr(sofa, opt)
    elif mandatory:
        assert hasattr(sofa, man) and not hasattr(sofa, opt)
    elif optional:
        assert not hasattr(sofa, man) and hasattr(sofa, opt)

    if verbose:
        if mandatory and optional:
            assert man in out and opt in out
        elif mandatory:
            assert man in out and opt not in out
        elif optional:
            assert man not in out and opt in out
    else:
        assert out == ""


def test_delete_entry():

    sofa = sf.Sofa("SimpleHeadphoneIR")
    assert hasattr(sofa, "GLOBAL_History")
    assert hasattr(sofa, "SourceManufacturer")
    # delete one optional attribute and variable
    sofa.delete("GLOBAL_History")
    sofa.delete("SourceManufacturer")
    # check if data were removed
    assert not hasattr(sofa, "GLOBAL_History")
    assert not hasattr(sofa, "SourceManufacturer")


def test__get_size_and_shape_of_string_var():

    # test with string
    S, shape = sf.Sofa._get_size_and_shape_of_string_var("four", "key")
    assert S == 4
    assert shape == (1, 1)

    # test with single string list
    S, shape = sf.Sofa._get_size_and_shape_of_string_var(["four"], "key")
    assert S == 4
    assert shape == (1, )

    # test with list of strings
    S, shape = sf.Sofa._get_size_and_shape_of_string_var(
        ["four", "fivee"], "key")
    assert S == 5
    assert shape == (2, )

    # test with numpy strings array
    S, shape = sf.Sofa._get_size_and_shape_of_string_var(
        np.array(["four", "fivee"], dtype="S256"), "key")
    assert S == 5
    assert shape == (2, )

    # test with wrong type
    with raises(TypeError, match="key must be a string"):
        sf.Sofa._get_size_and_shape_of_string_var(1, "key")


def test___mandatory():
    assert sf.Sofa._mandatory("rm")
    assert not sf.Sofa._mandatory("r")
    assert not sf.Sofa._mandatory(None)


def test___readonly():
    assert sf.Sofa._read_only("rm")
    assert not sf.Sofa._read_only("m")
    assert not sf.Sofa._read_only(None)
