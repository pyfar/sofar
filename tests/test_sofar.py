import sofar as sf
from sofar.sofar import (_get_size_and_shape_of_string_var,
                         _format_value_for_netcdf,
                         _format_value_from_netcdf)
import os
from tempfile import TemporaryDirectory
import pytest
import numpy as np
import numpy.testing as npt


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

    paths = sf.list_conventions(verbose=False, return_type="name_version")
    assert isinstance(paths, list)
    assert isinstance(paths[0], tuple)


def test_create_sofa():
    # test assertion for type of convention parameter
    with pytest.raises(TypeError, match="Convention must be a string"):
        sf.create_sofa(1)
    # test assertion for invalid conventions
    with pytest.raises(ValueError, match="Convention 'invalid' not found"):
        sf.create_sofa("invalid")

    # test a single conversion
    # (all conversions are test in test_roundtrip)
    name = sf.list_conventions(verbose=False, return_type="name")[0]
    sofa = sf.create_sofa(name)
    assert isinstance(sofa, dict)

    # test returning only mandatory fields
    sofa_all = sf.create_sofa("SimpleFreeFieldHRIR")
    sofa_man = sf.create_sofa("SimpleFreeFieldHRIR", True)
    assert len(sofa_all) > len(sofa_man)

    # test version parameter
    sofa = sf.create_sofa("GeneralTF")
    assert str(sofa["GLOBAL:SOFAConventionsVersion"]) == str(2)

    sofa = sf.create_sofa("GeneralTF", version="1.0")
    assert str(sofa["GLOBAL:SOFAConventionsVersion"]) == str(1.)


def test_update_dimensions():

    # test the default "latest"
    sofa_1 = sf.create_sofa("GeneralTF", version="1.0")
    sofa_2 = sofa_1.copy()
    with pytest.warns(UserWarning, match="Upgraded"):
        sf.update_api(sofa_2)
    assert float(sofa_1["GLOBAL:SOFAConventionsVersion"]) == 1.0
    assert float(sofa_2["GLOBAL:SOFAConventionsVersion"]) == 2.0

    # test "match"
    sofa_1 = sf.create_sofa("GeneralTF", version="1.0")
    sofa_2 = sofa_1.copy()
    sf.update_api(sofa_2, version="match")
    assert float(sofa_1["GLOBAL:SOFAConventionsVersion"]) == 1.0
    assert float(sofa_2["GLOBAL:SOFAConventionsVersion"]) == 1.0

    # test version string
    sofa_1 = sf.create_sofa("GeneralTF")
    sofa_2 = sofa_1.copy()
    with pytest.warns(UserWarning, match="Downgraded"):
        sf.update_api(sofa_2, version="1.0")
    assert float(sofa_1["GLOBAL:SOFAConventionsVersion"]) == 2.0
    assert float(sofa_2["GLOBAL:SOFAConventionsVersion"]) == 1.0

    # test detecting and adding missing mandatory fields
    sofa_1 = sf.create_sofa("GeneralTF")
    sofa_1.pop("GLOBAL:Conventions")
    with pytest.warns(UserWarning, match="Mandatory field GLOBAL:Conventions"):
        sf.update_api(sofa_1)


def test_set_value():
    # dummy SOFA dictionairy
    sofa = sf.create_sofa("SimpleFreeFieldHRIR")

    # set value by key
    sf.set_value(sofa, "ListenerPosition", [0, 0, 1])
    npt.assert_allclose(sofa["ListenerPosition"],
                        np.atleast_2d([0, 0, 1]))

    # set with protected key
    with pytest.raises(ValueError, match="'API' is read only"):
        sf.set_value(sofa, "API", [0, 0, 1])
    with pytest.raises(ValueError, match="'GLOBAL:Conventions' is read only"):
        sf.set_value(sofa, "GLOBAL:Conventions", [0, 0, 1])
    # set with invalid key
    with pytest.raises(ValueError, match="'Data.RIR' is an invalid key"):
        sf.set_value(sofa, "Data.RIR", [0, 0, 1])


def test_info(capfd):

    sofa = sf.create_sofa("SimpleFreeFieldHRIR")

    # test with wrong info string
    with pytest.raises(
            ValueError, match="info is invalid but must be in summary, "):
        sf.info(sofa, "invalid")

    # test default
    sf.info(sofa)
    out, _ = capfd.readouterr()
    assert out.startswith("SimpleFreeFieldHRIR 1.0 (SOFA version 2.0")
    assert "M = 1 (measurements)" in out

    # test listing all entry names
    sf.info(sofa, "all")
    out, _ = capfd.readouterr()
    assert "all entries:" in out
    assert "SourceUp" in out and "Data.IR" in out

    # test listing only mandatory entries
    sf.info(sofa, "mandatory")
    out, _ = capfd.readouterr()
    assert "mandatory entries:" in out
    assert "SourceUp" not in out

    # test listing only optional entries
    sf.info(sofa, "optional")
    out, _ = capfd.readouterr()
    assert "optional entries:" in out
    assert "Data.IR" not in out

    # test listing read only entries
    sf.info(sofa, "read only")
    out, _ = capfd.readouterr()
    assert "read only entries:" in out
    assert out.endswith("GLOBAL:DataType\n\n")

    # test listing default values
    sf.info(sofa, "default")
    out, _ = capfd.readouterr()
    assert "showing default:" in out
    assert "ListenerPosition\n\t[0, 0, 0]"

    # test listing default values
    sf.info(sofa, "dimensions")
    out, _ = capfd.readouterr()
    assert "showing dimensions:" in out
    assert "ListenerPosition\n\tIC, MC"

    # test listing default values
    sf.info(sofa, "comment")
    out, _ = capfd.readouterr()
    assert "showing comment:" in out
    assert "GLOBAL:SOFAConventions\n\tThis convention set is for HRIRs"


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
        sofa = sf.create_sofa(name)
        sf.write_sofa(os.path.join(temp_dir.name, name), sofa)
        sofa_r = sf.read_sofa(os.path.join(temp_dir.name, name))
        assert sf.compare_sofa(sofa, sofa_r, verbose=True, exclude="DATE")


def test_compare_sofa():

    sofa_a = sf.create_sofa("SimpleFreeFieldHRIR")

    # check invalid
    with pytest.raises(ValueError, match="exclude is"):
        sf.compare_sofa(sofa_a, sofa_a, exclude="wrong")

    # check identical dictionaries
    assert sf.compare_sofa(sofa_a, sofa_a.copy())

    # check different number of keys
    sofa_b = sofa_a.copy()
    sofa_b.pop("ReceiverPosition")
    with pytest.warns(UserWarning, match="not identical: sofa_a has"):
        is_identical = sf.compare_sofa(sofa_a, sofa_b)
        assert not is_identical

    # check different keys
    sofa_b = sofa_a.copy()
    sofa_b["PositionReceiver"] = sofa_b.pop("ReceiverPosition")
    with pytest.warns(UserWarning, match="not identical: sofa_a and sofa_b"):
        is_identical = sf.compare_sofa(sofa_a, sofa_b)
        assert not is_identical

    # check different value for attribute
    sofa_b = sofa_a.copy()
    sofa_b["GLOBAL:Conventions"] = "SOFAAA"
    with pytest.warns(UserWarning, match="not identical: different values for"):
        is_identical = sf.compare_sofa(sofa_a, sofa_b)
        assert not is_identical

    # check different value for variable
    sofa_b = sofa_a.copy()
    sofa_b["Data.SamplingRate"] = 96e3
    with pytest.warns(UserWarning, match="not identical: different values for"):
        is_identical = sf.compare_sofa(sofa_a, sofa_b)
        assert not is_identical


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
        "string", "test:attr", None, 12)
    assert value == "string"
    assert dtype == "attribute"

    # int that should be converted to a string
    value, dtype = _format_value_for_netcdf(
        1, "test:attr", None, 12)
    assert value == "1"
    assert dtype == "attribute"

    # float that should be converted to a string
    value, dtype = _format_value_for_netcdf(
        0.2, "test:attr", None, 12)
    assert value == "0.2"
    assert dtype == "attribute"

    # string and IS dimensions
    value, dtype = _format_value_for_netcdf(
        "string", "test.var", "IS", 12)
    assert value == np.array("string", dtype="S12")
    assert dtype == "S1"
    assert value.ndim == 2

    # single entry array and none Dimensions
    value, dtype = _format_value_for_netcdf(
        ["string"], "test.var", "IS", 12)
    assert value == np.array(["string"], dtype="S12")
    assert dtype == "S1"
    assert value.ndim == 2

    # array of strings
    value, dtype = _format_value_for_netcdf(
        [["a"], ["bc"]], "test.var", "MS", 12)
    assert all(value == np.array([["a"], ["bc"]], "S12"))
    assert dtype == "S1"
    assert value.ndim == 2

    # test with list
    value, dtype = _format_value_for_netcdf(
        [0, 0], "test.var", "MR", 12)
    npt.assert_allclose(value, np.array([0, 0])[np.newaxis, ])
    assert dtype == "f8"
    assert value.ndim == 2

    # test with numpy array
    value, dtype = _format_value_for_netcdf(
        np.array([0, 0]), "test.var", "MR", 12)
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
