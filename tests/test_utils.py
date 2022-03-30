import sofar as sf
from sofar.utils import (_compile_conventions,
                         _get_conventions)
import os
import json
from tempfile import TemporaryDirectory
import pytest
from pytest import raises
import numpy as np
from copy import deepcopy
from distutils import dir_util


def test_list_conventions(capfd):

    # check output to console using pytest default fixture capfd
    sf.list_conventions()
    out, _ = capfd.readouterr()
    assert "Available SOFA conventions:" in out


def test__get_conventions(capfd):

    # check the return type
    paths = _get_conventions(return_type="path")
    assert isinstance(paths, list)
    assert os.path.isfile(paths[0])
    assert "source" not in paths[0]
    assert paths[0].endswith(".json")
    out, _ = capfd.readouterr()
    assert out == ""

    paths = _get_conventions(return_type="path_source")
    assert isinstance(paths, list)
    assert os.path.isfile(paths[0])
    assert "source" in paths[0]
    assert paths[0].endswith(".csv")
    out, _ = capfd.readouterr()
    assert out == ""

    names = _get_conventions(return_type="name")
    assert isinstance(names, list)
    assert not os.path.isfile(names[0])

    names_versions = _get_conventions(return_type="name_version")
    assert isinstance(names_versions, list)
    assert isinstance(names_versions[0], tuple)

    with raises(ValueError, match="return_type None is invalid"):
        _get_conventions(return_type="None")


def test_update_conventions(capfd):

    # create temporary directory and copy existing conventions
    temp_dir = TemporaryDirectory()
    dir_util.copy_tree(
        os.path.join(os.path.dirname(__file__), "..", "sofar", "conventions"),
        temp_dir.name)

    # modify and delete selected conventions to verbose feedback
    os.remove(os.path.join(temp_dir.name, "source", "GeneralTF_2.0.csv"))
    with open(os.path.join(
            temp_dir.name, "source", "GeneralFIR_2.0.csv"), "w") as fid:
        fid.write("test")

    # first run to test if conventions were updated
    sf.update_conventions(conventions_path=temp_dir.name, assume_yes=True)
    out, _ = capfd.readouterr()
    assert "added new convention: GeneralTF_2.0.csv" in out
    assert "updated existing convention: GeneralFIR_2.0.csv" in out

    # second run to make sure that up to date conventions are not overwritten
    sf.update_conventions(conventions_path=temp_dir.name, assume_yes=True)
    out, _ = capfd.readouterr()
    assert "added" not in out
    assert "updated" not in out


def test__compile_conventions():
    """Test compiling the json conventions from the csv files."""

    # create temporary directory and copy existing source conventions
    temp_dir = TemporaryDirectory()
    os.mkdir(os.path.join(temp_dir.name, "source"))
    dir_util.copy_tree(os.path.join(
        os.path.dirname(__file__), "..", "sofar", "conventions", "source"),
        os.path.join(temp_dir.name, "source"))

    # compile conventions
    _compile_conventions(temp_dir.name)

    # get list of reference json files
    paths = _get_conventions("path")
    conventions = [os.path.split(path)[1] for path in paths]
    path = os.path.split(paths[0])[0]

    for convention in conventions:
        # load conventions
        ref = os.path.join(path, convention)
        with open(ref, "r") as file:
            ref_data = json.load(file)

        test = os.path.join(temp_dir.name, convention)
        with open(test, "r") as file:
            test_data = json.load(file)

        # compare conventions
        assert ref_data == test_data


def test_equals_global_parameters():

    sofa_a = sf.Sofa("SimpleFreeFieldHRIR")

    # check invalid
    with raises(ValueError, match="exclude is"):
        sf.equals(sofa_a, sofa_a, exclude="wrong")

    # check identical objects
    assert sf.equals(sofa_a, sofa_a)

    # check different number of keys
    sofa_b = deepcopy(sofa_a)
    sofa_b._protected = False
    delattr(sofa_b, "ReceiverPosition")
    sofa_b._protected = True
    with pytest.warns(UserWarning, match="not identical: sofa_a has"):
        is_identical = sf.equals(sofa_a, sofa_b)
        assert not is_identical

    # check different keys
    sofa_b = deepcopy(sofa_a)
    sofa_b._protected = False
    sofa_b.PositionReceiver = sofa_b.ReceiverPosition
    delattr(sofa_b, "ReceiverPosition")
    sofa_b._protected = True
    with pytest.warns(UserWarning, match="not identical: sofa_a and sofa_b"):
        is_identical = sf.equals(sofa_a, sofa_b)
        assert not is_identical

    # check mismatching data types
    sofa_b = deepcopy(sofa_a)
    sofa_b._protected = False
    sofa_b._convention["ReceiverPosition"]["type"] = "int"
    sofa_b._protected = True
    with pytest.warns(UserWarning, match="not identical: ReceiverPosition"):
        is_identical = sf.equals(sofa_a, sofa_b)
        assert not is_identical

    # check exclude GLOBAL attributes
    sofa_b = deepcopy(sofa_a)
    sofa_b._protected = False
    delattr(sofa_b, "GLOBAL_Version")
    sofa_b._protected = True
    is_identical = sf.equals(sofa_a, sofa_b, exclude="GLOBAL")
    assert is_identical

    # check exclude Date attributes
    sofa_b = deepcopy(sofa_a)
    sofa_b._protected = False
    delattr(sofa_b, "GLOBAL_DateModified")
    sofa_b._protected = True
    is_identical = sf.equals(sofa_a, sofa_b, exclude="DATE")
    assert is_identical

    # check exclude Date attributes
    sofa_b = deepcopy(sofa_a)
    sofa_b._protected = False
    delattr(sofa_b, "GLOBAL_DateModified")
    sofa_b._protected = True
    is_identical = sf.equals(sofa_a, sofa_b, exclude="ATTR")
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
def test_equals_attribute_values(value_a, value_b, attribute, fails):

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
            assert not sf.equals(sofa_a, sofa_b)
    else:
        assert sf.equals(sofa_a, sofa_b)
