import sofar as sf
from sofar.utils import (_get_conventions,
                         _verify_convention_and_version,
                         _atleast_nd,
                         _nd_newaxis)
from sofar.io import (_format_value_for_netcdf,
                      _format_value_from_netcdf)
import os
import ctypes
import pathlib
from tempfile import TemporaryDirectory
import pytest
import numpy as np
import numpy.testing as npt
import netCDF4
from netCDF4 import Dataset
from packaging.version import parse


def test_read_write_sofa():

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
    with pytest.raises(ValueError, match="test.sofa does not exist"):
        sf.read_sofa("test.sofa")

    # read file of unknown convention
    sofa = sf.Sofa("SimpleFreeFieldHRIR")
    sf.write_sofa(filename, sofa)
    with Dataset(filename, "r+", format="NETCDF4") as file:
        file.SOFAConventions = "Funky"
    with pytest.raises(ValueError, match="Convention 'Funky' does not exist"):
        sf.read_sofa(filename)

    # read file of unknown version (stored in file)
    sofa = sf.Sofa("SimpleFreeFieldHRIR")
    sf.write_sofa(filename, sofa)
    with Dataset(filename, "r+", format="NETCDF4") as file:
        file.SOFAConventionsVersion = "0.1"
    # ValueError when version should be matched
    with pytest.raises(ValueError,
                       match="v0.1 is not a valid SOFA Convention"):
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
    with pytest.raises(ValueError, match="The SOFA object could not be"):
        sf.read_sofa(filename)
    # data can be read without updating API
    sf.read_sofa(filename, verify=False)


def test_read_sofa_custom_data():
    """Test if sofa files with custom data are loaded correctly."""

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
        with pytest.raises(ValueError, match="Convention 'MadeUp' does not"):
            sf.read_sofa(file)
        sofa_read = sf.read_sofa_as_netcdf(file)
        sf.equals(sofa, sofa_read)


def test_write_sofa_outdated_version():
    """Test the warning for writing SOFA files with outdated versions."""

    # generate test data and directory
    tmp = TemporaryDirectory()
    sofa = sf.Sofa("GeneralTF", version="1.0")

    # write with outdated version
    with pytest.warns(UserWarning, match="Writing SOFA object with outdated"):
        sf.write_sofa(os.path.join(tmp.name, "outdated.sofa"), sofa)


def test_write_sofa_compression():
    """Test writing SOFA files with compression."""

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
    Cyclic test of create, write, read functions.

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

        # writing deprecated and proposed conventions is not tested
        if name in deprecations["GLOBAL:SOFAConventions"] or \
                parse(version) < parse('1.0'):
            sofa = sf.Sofa(name, mandatory, version, verify=False)
            # non stable conventions are not verified
            if parse(version) >= parse('1.0'):
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
    Test writing and reading multidimensional string variables (Writing
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


def _netcdf_attribute_type(filename, attribute, variable=None):
    """
    Get the netCDF type of an attribute from the netCDF C library that netCDF4
    is linked against. The netCDF4 Python API does not expose the type of
    attributes.

    Returns 2 for netCDF type 'char' (NC_CHAR) and 12 for
    netCDF type 'string' (NC_STRING).
    """

    # load the C functions through the netCDF4 extension module, which links
    # the netCDF C library. Skip if this is not possible, e.g., on Windows
    try:
        lib = ctypes.CDLL(netCDF4._netCDF4.__file__)
        nc_open, nc_close = lib.nc_open, lib.nc_close
        nc_inq_varid, nc_inq_atttype = lib.nc_inq_varid, lib.nc_inq_atttype
    except (OSError, AttributeError):
        pytest.skip("netCDF C library can not be accessed via ctypes")

    # open file in read mode (0 = NC_NOWRITE). The C functions return 0 on
    # success and write their results to the passed pointers
    ncid, varid, xtype = ctypes.c_int(), ctypes.c_int(-1), ctypes.c_int()
    assert nc_open(str(filename).encode(), 0, ctypes.byref(ncid)) == 0

    # query the attribute type and make sure the file is closed afterwards
    try:
        # get the variable id (varid -1 = NC_GLOBAL for global attributes)
        if variable is not None:
            assert nc_inq_varid(
                ncid, variable.encode(), ctypes.byref(varid)) == 0
        assert nc_inq_atttype(
            ncid, varid, attribute.encode(), ctypes.byref(xtype)) == 0
    finally:
        nc_close(ncid)

    return xtype.value


@pytest.mark.parametrize("text", ["Only ASCII text", "Möre than ASCII text"])
def test_write_netcdf_char(text):
    """
    Test that attributes and string variables are written as netCDF type
    'char' and UTF-8 encoded.
    """

    temp_dir = TemporaryDirectory()
    file = os.path.join(temp_dir.name, "HeadphoneIR.sofa")

    sofa = sf.Sofa("SimpleHeadphoneIR")
    # add dummy matrix that contains 2 measurements
    sofa.Data_IR = np.zeros((2, 2, 10))

    # add text to global attribute, variable attribute, and string variable
    sofa.GLOBAL_Comment = text
    sofa.add_attribute("SourcePosition_Comment", text)
    sofa.SourceManufacturer = [[text], ["b"]]

    # remove other string variables for simplicity
    delattr(sofa, "SourceModel")
    delattr(sofa, "ReceiverDescriptions")
    delattr(sofa, "EmitterDescriptions")
    delattr(sofa, "MeasurementDate")
    sf.write_sofa(file, sofa)

    # Test that attributes are of netCDF type 'char' (NC_CHAR = 2)
    # This must checked with netCDF and cannot be checked with sofar.
    assert _netcdf_attribute_type(file, "Comment") == 2
    assert _netcdf_attribute_type(file, "Comment", "SourcePosition") == 2

    # Test SOFA string variable
    with Dataset(file, "r", format="NETCDF4") as nc:
        # attributes contain the text
        assert nc.Comment == text
        assert nc["SourcePosition"].Comment == text

        # string variable is of netCDF type 'char' with S as last dimension
        assert nc["SourceManufacturer"].datatype == "S1"
        assert nc["SourceManufacturer"].dimensions[-1] == "S"

        # S is the number of bytes of the longest UTF-8 encoded string
        n_bytes = len(text.encode("utf-8"))
        assert nc.dimensions["S"].size == n_bytes

        # characters are the UTF-8 encoded bytes padded with null characters
        nc.set_auto_chartostring(False)
        characters = np.ma.filled(nc["SourceManufacturer"][:], b"")
        assert characters.tobytes() == \
            text.encode("utf-8") + b"b".ljust(n_bytes, b"\x00")


def test_read_netcdf_string():
    """
    Test reading attributes and string variables of netCDF type 'string' that
    are not written by sofar but can be contained in SOFA files written by
    other applications. Sofar reads those as well to be user friendly, despite
    they violate the AES69-2022 standard.
    """

    temp_dir = TemporaryDirectory()
    file = os.path.join(temp_dir.name, "HeadphoneIR.sofa")
    text = "Möre than ASCII"

    sofa = sf.Sofa("SimpleHeadphoneIR")
    sf.write_sofa(file, sofa)

    # add attributes and string variable of netCDF type 'string'
    with Dataset(file, "a", format="NETCDF4") as nc:
        nc.setncattr_string("Comment", text)
        nc["SourcePosition"].setncattr_string("Comment", text)
        variable = nc.createVariable("CustomStrings", str, ("M", ))
        variable[0] = text

    assert _netcdf_attribute_type(file, "Comment") == 12

    sofa_r = sf.read_sofa(file, verify=False, verbose=False)
    assert sofa_r.GLOBAL_Comment == text
    assert sofa_r.SourcePosition_Comment == text
    assert sofa_r.CustomStrings == text
    assert sofa_r._convention["CustomStrings"]["type"] == "string"


def test_format_value_for_netcdf():

    # string and None dimensions (a.k.a NETCDF attribute)
    value, dtype = _format_value_for_netcdf(
        "string", "test_attr", "attribute", None, 12)
    assert value == b"string"
    assert dtype == "attribute"

    # int that should be converted to a string
    value, dtype = _format_value_for_netcdf(
        1, "test_attr", "attribute", None, 12)
    assert value == b"1"
    assert dtype == "attribute"

    # float that should be converted to a string
    value, dtype = _format_value_for_netcdf(
        0.2, "test_attr", "attribute", None, 12)
    assert value == b"0.2"
    assert dtype == "attribute"

    # non-ASCII string that should be encoded as UTF-8
    value, dtype = _format_value_for_netcdf(
        "Möre than ASCII", "test_attr", "attribute", None, 12)
    assert value == "Möre than ASCII".encode("utf-8")
    assert dtype == "attribute"

    # string and IS dimensions
    value, dtype = _format_value_for_netcdf(
        "string", "TestVar", "string", "IS", 12)
    assert value.view("S12")[..., 0] == np.array("string", dtype="S12")
    assert dtype == "S1"
    assert value.shape == (1, 1, 12)

    # single entry array and none Dimensions
    value, dtype = _format_value_for_netcdf(
        ["string"], "TestVar", "string", "IS", 12)
    assert value.view("S12")[..., 0] == np.array(["string"], dtype="S12")
    assert dtype == "S1"
    assert value.shape == (1, 1, 12)

    # array of strings
    value, dtype = _format_value_for_netcdf(
        [["a"], ["bc"]], "TestVar", "string", "MS", 12)
    assert all(value.view("S12")[..., 0] == np.array([["a"], ["bc"]], "S12"))
    assert dtype == "S1"
    assert value.shape == (2, 1, 12)

    # non-ASCII string that should be encoded as UTF-8 (15 characters but 16
    # bytes because 'ö' is encoded with 2 bytes)
    value, dtype = _format_value_for_netcdf(
        "Möre than ASCII", "TestVar", "string", "IS", 16)
    assert value.view("S16")[..., 0] == "Möre than ASCII".encode("utf-8")
    assert dtype == "S1"
    assert value.shape == (1, 1, 16)

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
    with pytest.raises(ValueError, match="Unknown type int for TestVar"):
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

    # non-ASCII string (emulate NetCDF binary format of UTF-8 string)
    value_in = np.array(list("Möre than ASCII".encode("utf-8")), dtype="u1")
    value = _format_value_from_netcdf(value_in.view("S1"), "Some_Attribute")
    assert value == "Möre than ASCII"

    # array of strings with empty characters (emulate masked NetCDF data)
    value_in = np.ma.masked_equal(
        np.array([["a", "b"], ["c", ""]], dtype="S1"), b"")
    value = _format_value_from_netcdf(value_in, "Some_Attribute")
    assert all(value == np.array(["ab", "c"], dtype="U"))

    # array of strings (emulate NetCDF type string)
    value_in = np.array(["Möre than ASCII", "str2"], dtype="O")
    value = _format_value_from_netcdf(value_in, "Some_Attribute")
    assert all(value == np.array(["Möre than ASCII", "str2"], dtype="U"))

    # attributes are returned unchanged
    value = _format_value_from_netcdf("Möre than ASCII", "Some_Attribute")
    assert value == "Möre than ASCII"

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
    with pytest.raises(TypeError, match="Data_IR: value.dtype is complex"):
        _format_value_from_netcdf(
            np.array([44100], dtype="complex"), "Data_IR")


def test_verify_convention_and_version():

    # test with existing convention and version (no error returns None)
    out = _verify_convention_and_version("1.0", "GeneralTF")
    assert out is None

    # test assertions
    with pytest.raises(ValueError, match="Convention 'Funky' does not exist"):
        _verify_convention_and_version("1.0", "Funky")
    with pytest.raises(ValueError,
                       match="v1.1 is not a valid SOFA Convention"):
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
