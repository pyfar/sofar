import sofar as sf
from sofar.sofar import (_get_size_and_shape_of_string_var,
                         _format_value_for_netcdf,
                         _format_value_from_netcdf,
                         _is_mandatory, _is_read_only, _nd_array,
                         _verify_convention_and_version)
import os
from tempfile import TemporaryDirectory
import pytest
import numpy as np
import numpy.testing as npt
from copy import deepcopy
from netCDF4 import Dataset


def test_list_conventions(capfd):

    # check output to console using pytest default fixture capfd
    sf.list_conventions()
    out, _ = capfd.readouterr()
    assert "Available SOFA conventions:" in out

    sf.list_conventions(verbose=False)
    out, _ = capfd.readouterr()
    assert out == ""

    # check the return type
    paths = sf.list_conventions(verbose=False, return_type="path")
    assert isinstance(paths, list)
    assert os.path.isfile(paths[0])

    names = sf.list_conventions(verbose=False, return_type="name")
    assert isinstance(names, list)
    assert not os.path.isfile(names[0])

    names_versions = sf.list_conventions(
        verbose=False, return_type="name_version")
    assert isinstance(names_versions, list)
    assert isinstance(names_versions[0], tuple)

    with pytest.raises(ValueError, match="return_type None is invalid"):
        sf.list_conventions(verbose=False, return_type="None")


def test_create_sofa_object(capfd):
    # test assertion for type of convention parameter
    with pytest.raises(TypeError, match="Convention must be a string"):
        sf.Sofa(1)
    # test assertion for invalid conventions
    with pytest.raises(ValueError, match="Convention 'invalid' not found"):
        sf.Sofa("invalid")

    # test creation with defaults
    sofa = sf.Sofa("GeneralTF")
    assert isinstance(sofa, sf.sofar.Sofa)
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
    with pytest.raises(ValueError, match="Version 0.25 not found. Available"):
        sf.Sofa("GeneralTF", version="0.25")

    # test without updating the api
    sofa = sf.Sofa("GeneralTF", update_api=False)
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
    with pytest.raises(TypeError, match="GLOBAL_Version is a read only"):
        sofa.GLOBAL_Version = 1

    # set non-existing attribute
    with pytest.raises(TypeError, match="new is an invalid attribute"):
        sofa.new = 1


def test_delete_attributes_os_sofa_object():
    sofa = sf.Sofa("GeneralTF")

    # delete optional attribute
    delattr(sofa, "GLOBAL_ApplicationName")

    # delete mandatory attribute
    with pytest.raises(TypeError, match="GLOBAL_Version is a mandatory"):
        delattr(sofa, "GLOBAL_Version")

    # delete not existing attribute
    with pytest.raises(TypeError, match="new is not an attribute"):
        delattr(sofa, "new")


def test_update_api_in_sofa_object():

    # test the default "latest"
    sofa = sf.Sofa("GeneralTF", version="1.0")
    assert str(sofa.GLOBAL_SOFAConventionsVersion) == "1.0"
    with pytest.warns(UserWarning, match="Upgraded"):
        sofa.update_api()
    assert str(sofa.GLOBAL_SOFAConventionsVersion) == "2.0"

    # test "match"
    sofa = sf.Sofa("GeneralTF", version="1.0")
    assert str(sofa.GLOBAL_SOFAConventionsVersion) == "1.0"
    sofa.update_api(version="match")
    assert str(sofa.GLOBAL_SOFAConventionsVersion) == "1.0"

    # test downgrading
    sofa = sf.Sofa("GeneralTF")
    assert str(sofa.GLOBAL_SOFAConventionsVersion) == "2.0"
    with pytest.warns(UserWarning, match="Downgraded"):
        sofa.update_api(version="1.0")
    assert str(sofa.GLOBAL_SOFAConventionsVersion) == "1.0"

    # test missing default attribute
    sofa = sf.Sofa("GeneralTF")
    sofa._frozen = False
    delattr(sofa, "GLOBAL_Conventions")
    sofa._frozen = True
    with pytest.warns(UserWarning, match="Mandatory attribute GLOBAL_Conv"):
        sofa.update_api()
    assert sofa.GLOBAL_Conventions == "SOFA"

    # test attribute with wrong shape
    sofa = sf.Sofa("GeneralTF")
    sofa.ListenerPosition = 1
    with pytest.raises(ValueError, match=("The shape of ListenerPosition")):
        sofa.update_api()


def test_info(capfd):

    sofa = sf.Sofa("SimpleFreeFieldHRIR")

    # test with wrong info string
    with pytest.raises(
            ValueError, match="info='invalid' is invalid"):
        sofa.info("invalid")

    # test listing all entry names
    sofa.info("all")
    out, _ = capfd.readouterr()
    assert "all entries:" in out
    assert "SourceUp" in out and "Data_IR" in out

    # test listing only mandatory entries
    sofa.info("mandatory")
    out, _ = capfd.readouterr()
    assert "mandatory entries:" in out
    assert "SourceUp" not in out

    # test listing only optional entries
    sofa.info("optional")
    out, _ = capfd.readouterr()
    assert "optional entries:" in out
    assert "Data_IR" not in out

    # test listing read only entries
    sofa.info("read only")
    out, _ = capfd.readouterr()
    assert "read only entries:" in out
    assert out.endswith("GLOBAL_DataType\n\n")

    # test dimensions
    sofa.info("dimensions")
    out, _ = capfd.readouterr()
    assert out.startswith("SimpleFreeFieldHRIR 1.0 (SOFA version 2.0")
    assert "M = 1 (measurements)" in out

    # test listing default values
    sofa.info("default")
    out, _ = capfd.readouterr()
    assert "showing default:" in out
    assert "ListenerPosition\n\t[0, 0, 0]"

    # test listing default shapes
    sofa.info("shape")
    out, _ = capfd.readouterr()
    assert "showing shape:" in out
    assert "ListenerPosition\n\tIC, MC"

    # test listing comments values
    sofa.info("comment")
    out, _ = capfd.readouterr()
    assert "showing comment:" in out
    assert "GLOBAL_SOFAConventions\n\tThis convention set is for HRIRs"

    # list information for specific entry
    sofa.info("ListenerPosition")
    out, _ = capfd.readouterr()
    assert "ListenerPosition\n\ttype: double" in out
    assert "ListenerPosition_Type\n\ttype: attribute" in out
    assert "ListenerPosition_Units\n\ttype: attribute" in out


def test_read_sofa():

    temp_dir = TemporaryDirectory()
    filename = os.path.join(temp_dir.name, "test.sofa")
    sofa = sf.Sofa("SimpleFreeFieldHRIR")

    # test defaults
    sf.write_sofa(filename, sofa)
    sofa = sf.read_sofa(filename)
    assert hasattr(sofa, "_api")

    # reading without updating API
    sofa = sf.read_sofa(filename, update_api=False)
    assert not hasattr(sofa, "_api")

    # read non-existing file
    with pytest.raises(ValueError, match="test.sofa does not exist"):
        sf.read_sofa("test.sofa")

    # read file of unknown convention
    sofa = sf.Sofa("SimpleFreeFieldHRIR")
    sf.write_sofa(filename, sofa)
    with Dataset(filename, "r+", format="NETCDF4") as file:
        setattr(file, "SOFAConventions", "Funky")
    with pytest.raises(ValueError, match="File has unknown convention Funky"):
        sf.read_sofa(filename)

    # read file of unknown version
    sofa = sf.Sofa("SimpleFreeFieldHRIR")
    sf.write_sofa(filename, sofa)
    with pytest.raises(ValueError, match="Version not found"):
        sf.read_sofa(filename, version="0.25")

    # read file containing a variable with wrong shape
    sofa = sf.Sofa("SimpleFreeFieldHRIR")
    sf.write_sofa(filename, sofa)
    # create variable with wrong shape
    with Dataset(filename, "r+", format="NETCDF4") as file:
        file.createDimension('A', 10)
        var = file.createVariable("Data_IR", "f8", ('I', 'A'))
        var[:] = np.zeros((1, 10)).astype("double")
    # reading data with update API generates an error
    with pytest.raises(ValueError, match="The API could not be updated"):
        sf.read_sofa(filename)
    # data can be read without updating API
    sf.read_sofa(filename, update_api=False)


def test_roundtrip():
    """"
    Cyclic test of create, write, read functions

    1. create_sofa
    2. write_sofa
    3. read_sofa
    4. compare SOFA from 1. and 3.
    """

    temp_dir = TemporaryDirectory()
    names = sf.list_conventions(verbose=False, return_type="name")

    for name in names:
        print(f"Testing: {name}")
        file = os.path.join(temp_dir.name, name)
        sofa = sf.Sofa(name)
        sf.write_sofa(file, sofa)
        sofa_r = sf.read_sofa(file)
        identical = sf.compare_sofa(sofa, sofa_r, verbose=True, exclude="DATE")
        assert identical


def test_compare_sofa():

    sofa_a = sf.Sofa("SimpleFreeFieldHRIR")

    # check invalid
    with pytest.raises(ValueError, match="exclude is"):
        sf.compare_sofa(sofa_a, sofa_a, exclude="wrong")

    # check identical objects
    assert sf.compare_sofa(sofa_a, sofa_a)

    # check different number of keys
    sofa_b = deepcopy(sofa_a)
    sofa_b._frozen = False
    delattr(sofa_b, "ReceiverPosition")
    sofa_b._frozen = True
    with pytest.warns(UserWarning, match="not identical: sofa_a has"):
        is_identical = sf.compare_sofa(sofa_a, sofa_b)
        assert not is_identical

    # check different keys
    sofa_b = deepcopy(sofa_a)
    sofa_b._frozen = False
    sofa_b.PositionReceiver = sofa_b.ReceiverPosition
    delattr(sofa_b, "ReceiverPosition")
    sofa_b._frozen = True
    with pytest.warns(UserWarning, match="not identical: sofa_a and sofa_b"):
        is_identical = sf.compare_sofa(sofa_a, sofa_b)
        assert not is_identical

    # check different value for attribute
    sofa_b = deepcopy(sofa_a)
    sofa_b.Data_SamplingRate_Units = "kW"
    with pytest.warns(UserWarning, match="not identical: different values for"):
        is_identical = sf.compare_sofa(sofa_a, sofa_b)
        assert not is_identical

    # check different value for variable
    sofa_b = deepcopy(sofa_a)
    sofa_b.Data_SamplingRate = 96e3
    with pytest.warns(UserWarning, match="not identical: different values for"):
        is_identical = sf.compare_sofa(sofa_a, sofa_b)
        assert not is_identical

    # check exclude GLOBAL attributes
    sofa_b = deepcopy(sofa_a)
    sofa_b._frozen = False
    delattr(sofa_b, "GLOBAL_Version")
    sofa_b._frozen = True
    is_identical = sf.compare_sofa(sofa_a, sofa_b, exclude="GLOBAL")
    assert is_identical

    # check exclude Date attributes
    sofa_b = deepcopy(sofa_a)
    sofa_b._frozen = False
    delattr(sofa_b, "GLOBAL_DateModified")
    sofa_b._frozen = True
    is_identical = sf.compare_sofa(sofa_a, sofa_b, exclude="DATE")
    assert is_identical

    # check exclude Date attributes
    sofa_b = deepcopy(sofa_a)
    sofa_b._frozen = False
    delattr(sofa_b, "GLOBAL_DateModified")
    sofa_b._frozen = True
    is_identical = sf.compare_sofa(sofa_a, sofa_b, exclude="ATTR")
    assert is_identical


def test_get_size_and_shape_of_string_var():

    # test with string
    S, shape = _get_size_and_shape_of_string_var("four", "key")
    assert S == 4
    assert shape == (1, 1)

    # test with single string list
    S, shape = _get_size_and_shape_of_string_var(["four"], "key")
    assert S == 4
    assert shape == (1, )

    # test with list of strings
    S, shape = _get_size_and_shape_of_string_var(["four", "fivee"], "key")
    assert S == 5
    assert shape == (2, )

    # test with numpy strings array
    S, shape = _get_size_and_shape_of_string_var(
        np.array(["four", "fivee"], dtype="S256"), "key")
    assert S == 5
    assert shape == (2, )


def test_format_value_for_netcdf():

    # string and None dimensions (a.k.a NETCDF attribute)
    value, dtype = _format_value_for_netcdf(
        "string", "test_attr", "attribute", None, 12)
    assert value == "string"
    assert dtype == "attribute"

    # int that should be converted to a string
    value, dtype = _format_value_for_netcdf(
        1, "test_attr", "attribute", None, 12)
    assert value == "1"
    assert dtype == "attribute"

    # float that should be converted to a string
    value, dtype = _format_value_for_netcdf(
        0.2, "test_attr", "attribute", None, 12)
    assert value == "0.2"
    assert dtype == "attribute"

    # string and IS dimensions
    value, dtype = _format_value_for_netcdf(
        "string", "TestVar", "string", "IS", 12)
    assert value == np.array("string", dtype="S12")
    assert dtype == "S1"
    assert value.ndim == 2

    # single entry array and none Dimensions
    value, dtype = _format_value_for_netcdf(
        ["string"], "TestVar", "string", "IS", 12)
    assert value == np.array(["string"], dtype="S12")
    assert dtype == "S1"
    assert value.ndim == 2

    # array of strings
    value, dtype = _format_value_for_netcdf(
        [["a"], ["bc"]], "TestVar", "string", "MS", 12)
    assert all(value == np.array([["a"], ["bc"]], "S12"))
    assert dtype == "S1"
    assert value.ndim == 2

    # test with list
    value, dtype = _format_value_for_netcdf(
        [0, 0], "TestVar", "double", "MR", 12)
    npt.assert_allclose(value, np.array([0, 0])[np.newaxis, ])
    assert dtype == "f8"
    assert value.ndim == 2

    # test with numpy array
    value, dtype = _format_value_for_netcdf(
        np.array([0, 0]), "TestVar", "double", "MR", 12)
    npt.assert_allclose(value, np.array([0, 0])[np.newaxis, ])
    assert dtype == "f8"
    assert value.ndim == 2


def test_format_value_from_netcdf():

    # single string
    value = _format_value_from_netcdf(
        np.array(["string"], dtype="S6"), "Some:Attribute")
    assert value == "string"

    # array of strings
    value = _format_value_from_netcdf(
        np.array(["string1", "string2"], dtype="S7"), "Some:Attribute")
    assert all(value == np.array(["string1", "string2"], dtype="U"))

    # numerical array that can be scalar
    value = _format_value_from_netcdf(
        np.array([44100], dtype="float"), "Data.SamplingRate")
    assert value == 44100.

    # numerical array that can not be scalar
    value = _format_value_from_netcdf(
        np.array([44100], dtype="float"), "Data.IR")
    assert value == np.array(44100., dtype="float")

    # test with invalid data dyte
    with pytest.raises(TypeError, match="Data.IR: value.dtype is int32 but"):
        _format_value_from_netcdf(
            np.array([44100], dtype="int"), "Data.IR")


def test_is_mandatory():
    assert _is_mandatory("rm")
    assert not _is_mandatory("r")
    assert not _is_mandatory(None)


def test_is_readonly():
    assert _is_read_only("rm")
    assert not _is_read_only("m")
    assert not _is_read_only(None)


def test_verify_convention_and_version():

    # test different possibilities for version
    version = _verify_convention_and_version("latest", "1.0", "GeneralTF")
    assert version == "2.0"

    version = _verify_convention_and_version("2.0", "1.0", "GeneralTF")
    assert version == "2.0"

    version = _verify_convention_and_version("match", "1.0", "GeneralTF")
    assert version == "1.0"

    # test assertions
    with pytest.raises(ValueError, match="Convention Funky does not exist"):
        _verify_convention_and_version("latest", "1.0", "Funky")
    with pytest.raises(ValueError, match="Version 1.1 does not exist"):
        _verify_convention_and_version("match", "1.1", "GeneralTF")
    with pytest.raises(ValueError, match="Version 1.2 does not exist"):
        _verify_convention_and_version("1.2", "1.0", "GeneralTF")


def test_nd_array():
    # test with single dimension array
    for ndim in range(1, 6):
        array = _nd_array(1, ndim)
        assert array.ndim == ndim
        assert array.flatten() == np.array([1])

    # test with two-dimensional array
    for ndim in range(1, 6):
        array = _nd_array(np.atleast_2d(1), ndim)
        assert array.ndim == max(2, ndim)
        assert array.flatten() == np.array([1])
