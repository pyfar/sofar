import sofar as sf
from sofar.sofar import (_get_size_and_shape_of_string_var,
                         _format_value_for_netcdf)
import os
from pytest import raises
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
    with raises(TypeError, match="Convention must be a string"):
        sf.create_sofa(1)
    # test assertion for invalid conventions
    with raises(ValueError, match="Convention 'invalid' not found"):
        sf.create_sofa("invalid")

    # test conversion
    names = sf.list_conventions(verbose=False, return_type="name")
    for name in names:
        print(f"Testing: {name}")
        sofa = sf.create_sofa(name)
        assert isinstance(sofa, dict)

    # test returning only mandatory fields
    sofa_all = sf.create_sofa("SimpleFreeFieldHRIR")
    sofa_man = sf.create_sofa("SimpleFreeFieldHRIR", True)
    assert len(sofa_all) > len(sofa_man)


def test_set_value():
    # dummy SOFA dictionairy
    sofa = sf.create_sofa("SimpleFreeFieldHRIR")

    # set value by key
    sf.set_value(sofa, "ListenerPosition", [0, 0, 1])
    npt.assert_allclose(sofa["ListenerPosition"],
                        np.atleast_2d([0, 0, 1]))

    # set with protected key
    with raises(ValueError, match="'API' is read only"):
        sf.set_value(sofa, "API", [0, 0, 1])
    with raises(ValueError, match="'GLOBAL:Conventions' is read only"):
        sf.set_value(sofa, "GLOBAL:Conventions", [0, 0, 1])
    # set with invalid key
    with raises(ValueError, match="'Data.RIR' is an invalid key"):
        sf.set_value(sofa, "Data.RIR", [0, 0, 1])


def test_get_size_and_shape_of_string_var():

    # test with string
    S, shape = _get_size_and_shape_of_string_var("four", "key")
    assert S == 4
    assert shape == (1, 4)

    # test with list of strings
    S, shape = _get_size_and_shape_of_string_var(["four", "fivee"], "key")
    assert S == 5
    assert shape == (2, 5)

    # test with numpy strings array
    S, shape = _get_size_and_shape_of_string_var(
        np.array(["four", "fivee"], dtype="S256"), "key")
    assert S == 5
    assert shape == (2, 5)


def test_format_value_for_netcdf():

    # string and None dimensions
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

    # single entry array and none Dimensions
    value, dtype = _format_value_for_netcdf(
        ["string"], "test.var", "IS", 12)
    assert value == np.array("string", dtype="S12")
    assert dtype == "S1"

    # array of strings
    value, dtype = _format_value_for_netcdf(
        [["a"], ["bc"]], "test.var", "MS", 12)
    assert all(value == np.array([["a"], ["bc"]], "S12"))
    assert dtype == "S1"

    # test with list
    value, dtype = _format_value_for_netcdf(
        [0, 0], "test.var", "MR", 12)
    npt.assert_allclose(value, np.array([0, 0])[np.newaxis, ])
    assert dtype == "f8"

    # test with numpy array
    value, dtype = _format_value_for_netcdf(
        np.array([0, 0]), "test.var", "MR", 12)
    npt.assert_allclose(value, np.array([0, 0])[np.newaxis, ])
    assert dtype == "f8"
