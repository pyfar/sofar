import sofar as sf
from sofar.sofar import (_format_value_for_netcdf,
                         _format_value_from_netcdf,
                         _nd_array,
                         _nd_newaxis,
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
    with pytest.raises(TypeError, match="GLOBAL_Version is a read only"):
        sofa.GLOBAL_Version = 1

    # set non-existing attribute
    with pytest.raises(TypeError, match="new is an invalid attribute"):
        sofa.new = 1


def test_sofa_delete_attribute():
    sofa = sf.Sofa("GeneralTF")

    # delete optional attribute
    delattr(sofa, "GLOBAL_ApplicationName")

    # delete mandatory attribute
    with pytest.raises(TypeError, match="GLOBAL_Version is a mandatory"):
        delattr(sofa, "GLOBAL_Version")

    # delete not existing attribute
    with pytest.raises(TypeError, match="new is not an attribute"):
        delattr(sofa, "new")


def test_sofa_verify():

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

    # test missing default attribute
    sofa = sf.Sofa("GeneralTF")
    sofa._protected = False
    delattr(sofa, "GLOBAL_Conventions")
    sofa._protected = True
    with pytest.warns(UserWarning, match="Mandatory attribute GLOBAL_Conv"):
        sofa.verify()
    assert sofa.GLOBAL_Conventions == "SOFA"

    # test attribute with wrong shape
    sofa = sf.Sofa("GeneralTF")
    sofa.ListenerPosition = 1
    with pytest.raises(ValueError, match=("The shape of ListenerPosition")):
        sofa.verify()

    # test invalid data for netCDF attribute
    sofa = sf.Sofa("GeneralTF")
    sofa.GLOBAL_History = 1
    with pytest.raises(ValueError, match="GLOBAL_History must be a string"):
        sofa.verify()

    # test invalid data for netCDF double variable
    sofa = sf.Sofa("GeneralTF")
    sofa.Data_Real = np.array("test")
    with pytest.raises(ValueError, match="Data_Real can be of dtype"):
        sofa.verify()

    sofa.Data_Real = [1, 1., 1+1j, "1"]
    with pytest.raises(ValueError, match="Data_Real can be of dtype int"):
        sofa.verify()

    # test valid data
    sofa.Data_Real = np.array([1])
    sofa.verify()
    sofa.Data_Real = [1]
    sofa.verify()

    # test invalid data for netCDF string variable
    sofa = sf.Sofa("SimpleHeadphoneIR")
    sofa.SourceModel = 1
    with pytest.raises(ValueError, match="SourceModel can be of type"):
        sofa.verify()

    sofa.SourceModel = np.array(1)
    with pytest.raises(ValueError, match="SourceModel can be of dtype"):
        sofa.verify()

    # test valid data
    sofa.SourceModel = ["test"]
    sofa.verify()
    sofa.SourceModel = np.array(["test"])
    sofa.verify()


def test_dimensions(capfd):

    # test FIR Data
    sofa = sf.Sofa("GeneralFIR")
    sofa.dimensions
    out, _ = capfd.readouterr()
    assert out.startswith("GeneralFIR 2.0 (SOFA version 2.0")
    assert "N = 1 (samples)" in out

    # test TF Data
    sofa = sf.Sofa("GeneralTF")
    sofa.dimensions
    out, _ = capfd.readouterr()
    assert out.startswith("GeneralTF 2.0 (SOFA version 1.0")
    assert "N = 1 (frequencies)" in out

    # test SOS Data
    sofa = sf.Sofa("SimpleFreeFieldSOS")
    sofa.dimensions
    out, _ = capfd.readouterr()
    assert out.startswith("SimpleFreeFieldSOS 1.0 (SOFA version 1.0")
    assert "N = 6 (SOS coefficients)" in out


def test_info(capfd):

    sofa = sf.Sofa("SimpleFreeFieldHRIR")

    # test with wrong info string
    with pytest.raises(
            ValueError, match="info='invalid' is invalid"):
        sofa.info("invalid")

    # test listing all entry names
    for info in ["all", "mandatory", "optional", "read only", "data"]:
        sofa.info(info)
        out, _ = capfd.readouterr()
        assert f"showing {info} entries" in out

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
    sofa = sf.read_sofa(filename, verify=False)
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
    with pytest.raises(ValueError, match="The SOFA object could not be"):
        sf.read_sofa(filename)
    # data can be read without updating API
    sf.read_sofa(filename, verify=False)


def test_write_sofa_compression():
    """Test writing SOFA files with compression"""

    # create temporary directory
    temp_dir = TemporaryDirectory()

    # create test data
    sofa = sf.Sofa('SimpleFreeFieldHRIR')
    sofa.Data_IR = np.zeros((1, 2, 2048))
    sofa.Data_IR[0, 0] = np.array([1, 0, -1, 0] * 512)

    filesize = None

    for compression in range(10):
        # write with current compression level
        filename = os.path.join(temp_dir.name, f"test_{0}.sofa")
        sf.write_sofa(filename, sofa, compression=compression)

        # get and compare the file sizes
        print(f"Assessing compression level {compression}")
        if compression > 0:
            assert os.stat(filename).st_size <= filesize
        filesize = os.stat(filename).st_size


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


def test_compare_sofa_global_parameters():

    sofa_a = sf.Sofa("SimpleFreeFieldHRIR")

    # check invalid
    with pytest.raises(ValueError, match="exclude is"):
        sf.compare_sofa(sofa_a, sofa_a, exclude="wrong")

    # check identical objects
    assert sf.compare_sofa(sofa_a, sofa_a)

    # check different number of keys
    sofa_b = deepcopy(sofa_a)
    sofa_b._protected = False
    delattr(sofa_b, "ReceiverPosition")
    sofa_b._protected = True
    with pytest.warns(UserWarning, match="not identical: sofa_a has"):
        is_identical = sf.compare_sofa(sofa_a, sofa_b)
        assert not is_identical

    # check different keys
    sofa_b = deepcopy(sofa_a)
    sofa_b._protected = False
    sofa_b.PositionReceiver = sofa_b.ReceiverPosition
    delattr(sofa_b, "ReceiverPosition")
    sofa_b._protected = True
    with pytest.warns(UserWarning, match="not identical: sofa_a and sofa_b"):
        is_identical = sf.compare_sofa(sofa_a, sofa_b)
        assert not is_identical

    # check mismatching data types
    sofa_b = deepcopy(sofa_a)
    sofa_b._protected = False
    sofa_b._convention["ReceiverPosition"]["type"] = "int"
    sofa_b._protected = True
    with pytest.warns(UserWarning, match="not identical: ReceiverPosition"):
        is_identical = sf.compare_sofa(sofa_a, sofa_b)
        assert not is_identical

    # check exclude GLOBAL attributes
    sofa_b = deepcopy(sofa_a)
    sofa_b._protected = False
    delattr(sofa_b, "GLOBAL_Version")
    sofa_b._protected = True
    is_identical = sf.compare_sofa(sofa_a, sofa_b, exclude="GLOBAL")
    assert is_identical

    # check exclude Date attributes
    sofa_b = deepcopy(sofa_a)
    sofa_b._protected = False
    delattr(sofa_b, "GLOBAL_DateModified")
    sofa_b._protected = True
    is_identical = sf.compare_sofa(sofa_a, sofa_b, exclude="DATE")
    assert is_identical

    # check exclude Date attributes
    sofa_b = deepcopy(sofa_a)
    sofa_b._protected = False
    delattr(sofa_b, "GLOBAL_DateModified")
    sofa_b._protected = True
    is_identical = sf.compare_sofa(sofa_a, sofa_b, exclude="ATTR")
    assert is_identical


@pytest.mark.parametrize("value_a, value_b, attribute, fails", [
    (1, "1", "GLOBAL_SOFAConventionsVersion", False),
    (1, "1.0", "GLOBAL_SOFAConventionsVersion", False),
    (1., "1", "GLOBAL_SOFAConventionsVersion", False),
    ("1", "2", "GLOBAL_SOFAConventionsVersion", True),
    ([[1, 2]], [1, 2], "Data_IR", False),
    ([[1, 2]], [1, 3], "Data_IR", True),
    ("HD 650", ["HD 650"], "SourceModel", False),
    ("HD 650", np.array(["HD 650"], dtype="U"), "SourceModel", False),
    ("HD 650", np.array(["HD 650"], dtype="S"), "SourceModel", False),
    ("HD 650", "HD-650", "SourceModel", True)
])
def test_compare_sofa_attribute_values(value_a, value_b, attribute, fails):

    # generate SOFA objects (SimpleHeadphoneIR has string variables)
    sofa_a = sf.Sofa("SimpleHeadphoneIR")
    sofa_a._protected = False
    sofa_b = deepcopy(sofa_a)

    # set parameters
    setattr(sofa_a, attribute, value_a)
    sofa_a._protected = True
    setattr(sofa_b, attribute, value_b)
    sofa_b._protected = True

    # compare
    if fails:
        with pytest.warns(UserWarning):
            assert not sf.compare_sofa(sofa_a, sofa_b)
    else:
        assert sf.compare_sofa(sofa_a, sofa_b)


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
    sofa.add_attribute("Temperature_Units", "degree Celsius")
    assert sofa.Temperature_Units == "degree Celsius"

    # check if everything can be verified and written, and read correctly
    sf.write_sofa(os.path.join(tmp_dir.name, "tmp"), sofa)
    sofa_read = sf.read_sofa(os.path.join(tmp_dir.name, "tmp"))
    assert sf.compare_sofa(sofa, sofa_read)

    # test deleting an entry
    delattr(sofa, "Temperature_Units")
    assert not hasattr(sofa, "Temperature_Units")
    assert "Temperature_Units" not in sofa._custom

    # test assertions
    # add existing entry
    with pytest.raises(ValueError, match="Entry Temperature already exists"):
        sofa.add_variable("Temperature", 25.1, "double", "MI")
    # entry violating the naming convention
    with pytest.raises(ValueError, match="underscores '_' in the name"):
        sofa.add_variable("Temperature_Celsius", 25.1, "double", "MI")
    # entry with wrong type
    with pytest.raises(ValueError, match="dtype is float but must be"):
        sofa.add_variable("TemperatureCelsius", 25.1, "float", "MI")
    # variable without dimensions
    with pytest.raises(ValueError, match="dimensions must be provided"):
        sofa.add_variable("TemperatureCelsius", 25.1, "double", None)
    # invalid dimensins
    with pytest.warns(UserWarning, match="Added custom dimension T"):
        sofa.add_variable("TemperatureCelsius", [25.1, 25.2], "double", "T")


def test_get_size_and_shape_of_string_var():

    # test with string
    S, shape = sf.Sofa._get_size_and_shape_of_string_var("four", "key")
    assert S == 4
    assert shape == (1, 1)

    # test with single string list
    S, shape = sf.Sofa._get_size_and_shape_of_string_var(["four"], "key")
    assert S == 4
    assert shape == (1, )

    # test with list of strings
    S, shape = sf.Sofa._get_size_and_shape_of_string_var(["four", "fivee"], "key")
    assert S == 5
    assert shape == (2, )

    # test with numpy strings array
    S, shape = sf.Sofa._get_size_and_shape_of_string_var(
        np.array(["four", "fivee"], dtype="S256"), "key")
    assert S == 5
    assert shape == (2, )

    # test with wrong type
    with pytest.raises(TypeError, match="key must be a string"):
        sf.Sofa._get_size_and_shape_of_string_var(1, "key")


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

    # unkonw data type
    with pytest.raises(ValueError, match="Unknown type int for TestVar"):
        value, dtype = _format_value_for_netcdf(1, "TestVar", "int", "MR", 12)


def test_format_value_from_netcdf():

    # single string
    value = _format_value_from_netcdf(
        np.array(["string"], dtype="S6"), "Some_Attribute")
    assert value == "string"

    # array of strings
    value = _format_value_from_netcdf(
        np.array(["string1", "string2"], dtype="S7"), "Some_Attribute")
    assert all(value == np.array(["string1", "string2"], dtype="U"))

    # numerical array that can be scalar
    value = _format_value_from_netcdf(
        np.array([44100], dtype="float"), "Data_SamplingRate")
    assert value == 44100.

    # numerical array that can not be scalar
    value = _format_value_from_netcdf(
        np.array([44100], dtype="float"), "Data_IR")
    assert value == np.array(44100., dtype="float")

    # masked array with missing data
    array = np.ma.masked_array([1, 2], mask=[0, 1], dtype="float")
    with pytest.warns(UserWarning, match="Entry Data_IR contains missing"):
        value = _format_value_from_netcdf(array, "Data_IR")
    npt.assert_allclose(value, array)

    # test with invalid data dtype
    with pytest.raises(TypeError, match="Data_IR: value.dtype is complex"):
        _format_value_from_netcdf(
            np.array([44100], dtype="complex"), "Data_IR")


def test_is_mandatory():
    assert sf.Sofa._mandatory("rm")
    assert not sf.Sofa._mandatory("r")
    assert not sf.Sofa._mandatory(None)


def test_is_readonly():
    assert sf.Sofa._read_only("rm")
    assert not sf.Sofa._read_only("m")
    assert not sf.Sofa._read_only(None)


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


def test_nd_newaxis():
    assert _nd_newaxis([1, 2, 3, 4, 5, 6], 2).shape == (6, 1)
