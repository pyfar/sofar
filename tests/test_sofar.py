import sofar as sf
from sofar.sofar import _get_size_and_shape_of_string_var
import os
from pytest import raises
import numpy as np
import numpy.testing as npt


def test_list_conventions(capfd):

    # check output to console using pytest default fixture capfd
    sf.list_conventions()
    out, _ = capfd.readouterr()
    assert "Available SOFA conventions:" in out

    sf.list_conventions(print_conventions=False)
    out, _ = capfd.readouterr()
    assert out == ""

    # check the return type
    paths = sf.list_conventions(print_conventions=False, return_paths=True)
    assert isinstance(paths, list)
    assert os.path.isfile(paths[0])


def test_create_sofa():
    # test assertion for type of convention parameter
    with raises(TypeError, match="Convention must be a string"):
        sf.create_sofa(1)
    # test assertion for invalid conventions
    with raises(ValueError, match="Convention 'invalid' not found"):
        sf.create_sofa("invalid")

    # test conversion
    paths = sf.list_conventions(print_conventions=False, return_paths=True)
    for path in paths:
        name = os.path.basename(path).split(sep="_")[0]
        print(f"Testing: {name}")
        convention = sf.create_sofa(name)
        assert isinstance(convention, dict)

    # test returning only mandatory fields
    convention_all = sf.create_sofa("SimpleFreeFieldHRIR")
    convention_man = sf.create_sofa("SimpleFreeFieldHRIR", True)
    assert len(convention_all) > len(convention_man)


def test_set_value():
    # dummy convention
    convention = sf.create_sofa("SimpleFreeFieldHRIR")

    # set value by key
    sf.set_value(convention, "ListenerPosition", [0, 0, 1])
    npt.assert_allclose(convention["ListenerPosition"],
                        np.atleast_2d([0, 0, 1]))

    # set with protected key
    with raises(ValueError, match="'API' is read only"):
        sf.set_value(convention, "API", [0, 0, 1])
    with raises(ValueError, match="'GLOBAL:Conventions' is read only"):
        sf.set_value(convention, "GLOBAL:Conventions", [0, 0, 1])
    # set with invalid key
    with raises(ValueError, match="'Data.RIR' is an invalid key"):
        sf.set_value(convention, "Data.RIR", [0, 0, 1])


# def test_updated_api():
#     sofa = sf.create_sofa("FreeFieldDirectivityTF")

#     # check initial assignment
#     assert sofa["API"]["M"] == 1


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
