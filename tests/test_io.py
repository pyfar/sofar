import sofar as sf
from sofar.utils import (_get_conventions,
                         _verify_convention_and_version,
                         _atleast_nd,
                         _nd_newaxis)
from sofar.io import (_format_value_for_netcdf,
                      _format_value_from_netcdf)
import os
import pathlib
from tempfile import TemporaryDirectory
import pytest
from pytest import raises
import numpy as np
import numpy.testing as npt
from netCDF4 import Dataset


def test_read_write_sofa(capfd):

    temp_dir = TemporaryDirectory()
    filename = os.path.join(temp_dir.name, "test.sofa")
    sofa = sf.Sofa("SimpleFreeFieldHRIR")

    # test defaults
    sf.write_sofa(filename, sofa)
    sofa = sf.read_sofa(filename)
    assert hasattr(sofa, "_api")

    # test with path object
    sf.write_sofa(pathlib.Path(filename), sofa)
    sofa = sf.read_sofa(pathlib.Path(filename))
    assert hasattr(sofa, "_api")

    # reading without updating API
    sofa = sf.read_sofa(filename, verify=False)
    assert not hasattr(sofa, "_api")

    # read non-existing file
    with raises(ValueError, match="test.sofa does not exist"):
        sf.read_sofa("test.sofa")

    # read file of unknown convention
    sofa = sf.Sofa("SimpleFreeFieldHRIR")
    sf.write_sofa(filename, sofa)
    with Dataset(filename, "r+", format="NETCDF4") as file:
        setattr(file, "SOFAConventions", "Funky")
    with raises(ValueError, match="Convention 'Funky' does not exist"):
        sf.read_sofa(filename)

    # read file of unknown version (stored in file)
    sofa = sf.Sofa("SimpleFreeFieldHRIR")
    sf.write_sofa(filename, sofa)
    with Dataset(filename, "r+", format="NETCDF4") as file:
        setattr(file, "SOFAConventionsVersion", "0.1")
    # ValueError when version should be matched
    with raises(ValueError, match="v0.1 is not a valid SOFA Convention"):
        sf.read_sofa(filename)

    # read file containing a variable with wrong shape
    sofa = sf.Sofa("SimpleFreeFieldHRIR")
    sf.write_sofa(filename, sofa)
    # create variable with wrong shape
    with Dataset(filename, "r+", format="NETCDF4") as file:
        file.createDimension('A', 10)
        var = file.createVariable("Data_IR", "f8", ('I', 'A'))
        var[:] = np.zeros((1, 10)).astype("double")
    # reading data with update API generates an error
    with raises(ValueError, match="The SOFA object could not be"):
        sf.read_sofa(filename)
    # data can be read without updating API
    sf.read_sofa(filename, verify=False)


def test_read_sofa_custom_data():
    """Test if sofa files with custom data are loaded correctly"""

    temp_dir = TemporaryDirectory()
    filename = os.path.join(temp_dir.name, "test.sofa")
    sofa = sf.Sofa("SimpleFreeFieldHRIR")

    # GLOBAL attribute
    sofa.add_attribute('GLOBAL_Warming', 'critical')
    sf.write_sofa(filename, sofa)
    sofa = sf.read_sofa(filename)
    assert sofa.GLOBAL_Warming == 'critical'


def test_read_netcdf():
    tmp = TemporaryDirectory()
    files = [os.path.join(tmp.name, "invalid.sofa"),
             os.path.join(tmp.name, "invalid.netcdf")]

    # create data with invalid SOFA convention and version
    sofa = sf.Sofa("GeneralTF")
    sofa.protected = False
    sofa.GLOBAL_SOFAConventions = "MadeUp"
    sofa.protected = True

    # test reading
    for file in files:
        # write data
        sf.io._write_sofa(file, sofa, verify=False)
        # can not be read with read_sofa
        with raises(ValueError):
            sf.read_sofa(file)
        sofa_read = sf.read_sofa_as_netcdf(file)
        sf.equals(sofa, sofa_read)


def test_write_sofa_outdated_version():
    """Test the warning for writing SOFA files with outdated versions"""

    # generate test data and directory
    tmp = TemporaryDirectory()
    sofa = sf.Sofa("GeneralTF", version="1.0")

    # write with outdated version
    with pytest.warns(UserWarning, match="Writing SOFA object with outdated"):
        sf.write_sofa(os.path.join(tmp.name, "outdated.sofa"), sofa)


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


# mandatory=True can not be tested because some conventions have default values
# that have optional variables as dependencies
@pytest.mark.parametrize("mandatory", [(False)])
def test_roundtrip(mandatory):
    """"
    Cyclic test of create, write, read functions

    1. create_sofa
    2. write_sofa
    3. read_sofa
    4. compare SOFA from 1. and 3.
    """

    temp_dir = TemporaryDirectory()
    names_versions = _get_conventions(return_type="name_version")

    _, _, deprecations, _ = sf.Sofa._verification_rules()

    for name, version in names_versions:
        print(f"Testing: {name} {version}")

        if name in deprecations["GLOBAL:SOFAConventions"]:
            # deprecated conventions can not be written
            sofa = sf.Sofa(name, mandatory, version, verify=False)
            with pytest.warns(UserWarning, match="deprecations"):
                sofa.verify(mode="read")
        else:
            # test full round-trip for other conventions
            file = os.path.join(temp_dir.name, name + ".sofa")
            sofa = sf.Sofa(name, mandatory, version)
            sf.write_sofa(file, sofa)
            sofa_r = sf.read_sofa(file)
            identical = sf.equals(sofa, sofa_r, verbose=True, exclude="DATE")
            assert identical


def test_roundtrip_multidimensional_string_variable():
    """
    Test writing and reading multidimensional string variables (Wringting
    string variables with one dimension is done in the other roundtrip test).
    """

    temp_dir = TemporaryDirectory()
    file = os.path.join(temp_dir.name, "HeadphoneIR.sofa")

    sofa = sf.Sofa("SimpleHeadphoneIR")
    # add dummy matrix that contains 4 measurements
    sofa.Data_IR = np.zeros((4, 2, 10))
    # add (4, 1) string variable
    sofa.SourceManufacturer = [["someone"], ["else"], ["did"], ["this"]]
    # remove other string variables for simplicity
    delattr(sofa, "SourceModel")
    delattr(sofa, "ReceiverDescriptions")
    delattr(sofa, "EmitterDescriptions")
    delattr(sofa, "MeasurementDate")

    # read write and assert
    sf.write_sofa(file, sofa)
    sofa_r = sf.read_sofa(file)

    identical = sf.equals(sofa, sofa_r, exclude="DATE")
    assert identical


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

    # unknown data type
    with raises(ValueError, match="Unknown type int for TestVar"):
        value, dtype = _format_value_for_netcdf(1, "TestVar", "int", "MR", 12)


def test_format_value_from_netcdf():

    # single string (emulate NetCDF binary format)
    value_in = np.array(["s", "t", "r"], dtype="S1")
    value = _format_value_from_netcdf(value_in, "Some_Attribute")
    assert value == "str"

    # array of strings (emulate NetCDF binary format)
    value_in = np.array([["s", "t", "r", "1"], ["s", "t", "r", "2"]],
                        dtype="S1")
    value = _format_value_from_netcdf(value_in, "Some_Attribute")
    assert all(value == np.array(["str1", "str2"], dtype="U"))

    # single string (emulate NetCDF ascii encoding)
    value_in = np.array(["str"], dtype="U")
    value = _format_value_from_netcdf(value_in, "Some_Attribute")
    assert value == "str"

    # array of strings (emulate NetCDF binary format)
    value_in = np.array(["str1", "str2"], dtype="U")
    value = _format_value_from_netcdf(value_in, "Some_Attribute")
    assert all(value == np.array(["str1", "str2"], dtype="U"))

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
    with raises(TypeError, match="Data_IR: value.dtype is complex"):
        _format_value_from_netcdf(
            np.array([44100], dtype="complex"), "Data_IR")


def test_verify_convention_and_version():

    # test with existing convention and version (no error returns None)
    out = _verify_convention_and_version("1.0", "GeneralTF")
    assert out is None

    # test assertions
    with raises(ValueError, match="Convention 'Funky' does not exist"):
        _verify_convention_and_version("1.0", "Funky")
    with raises(ValueError, match="v1.1 is not a valid SOFA Convention"):
        _verify_convention_and_version("1.1", "GeneralTF")


def test_atleast_nd():
    # test with single dimension array
    for ndim in range(1, 6):
        array = _atleast_nd(1, ndim)
        assert array.ndim == ndim
        assert array.flatten() == np.array([1])

    # test with two-dimensional array
    for ndim in range(1, 6):
        array = _atleast_nd(np.atleast_2d(1), ndim)
        assert array.ndim == max(2, ndim)
        assert array.flatten() == np.array([1])


def test_nd_newaxis():
    assert _nd_newaxis([1, 2, 3, 4, 5, 6], 2).shape == (6, 1)
