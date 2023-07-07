import shutil
import sofar as sf
from sofar.utils import _get_conventions
from sofar.update_conventions import _compile_conventions, _check_congruency
import os
import json
from tempfile import TemporaryDirectory
import pytest
from pytest import raises
import numpy as np
from copy import deepcopy
import warnings


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
    assert paths[0].endswith(".json")
    out, _ = capfd.readouterr()
    assert out == ""

    paths = _get_conventions(return_type="path_source")
    assert isinstance(paths, list)
    assert os.path.isfile(paths[0])
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


@pytest.mark.parametrize('branch', ['master', 'development'])
def test__congruency(capfd, branch):
    """
    Check if conventions from SOFAToolbox and sofaconventions.org are
    identical.
    """
    out, _ = capfd.readouterr()
    _check_congruency(branch=branch)
    out, _ = capfd.readouterr()
    if out != "":
        warnings.warn(out, Warning)


def test_update_conventions(capfd):

    # create temporary directory and copy existing conventions
    temp_dir = TemporaryDirectory()
    work_dir = os.path.join(temp_dir.name, "sofa_conventions", "conventions")
    shutil.copytree(
        os.path.join(
            os.path.dirname(__file__), "..", "sofar", "sofa_conventions"),
        os.path.join(temp_dir.name, "sofa_conventions"))

    # delete standardized GeneralTF_2.0 to test adding
    os.remove(os.path.join(work_dir, "GeneralTF_2.0.csv"))
    os.remove(os.path.join(work_dir, "GeneralTF_2.0.json"))
    # modify standardized GeneralFIR_1.0 to test updating
    with open(os.path.join(work_dir, "GeneralFIR_1.0.csv"), "w") as fid:
        fid.write("modified")
    # move MultiSpeakerBRIR_0.3 to standardized to test deprecation
    os.rename(
        os.path.join(work_dir, "deprecated", "MultiSpeakerBRIR_0.3.csv"),
        os.path.join(work_dir, "MultiSpeakerBRIR_0.3.csv"))
    os.rename(
        os.path.join(work_dir, "deprecated", "MultiSpeakerBRIR_0.3.json"),
        os.path.join(work_dir, "MultiSpeakerBRIR_0.3.json"))
    # modify deprecated convention to test updating
    with open(os.path.join(work_dir, "deprecated",
                           "SimpleFreeFieldHRIR_0.4.csv"), "w") as fid:
        fid.write("modified")
    # delete deprecated GeneralTF_2.0 to test adding
    os.remove(os.path.join(
        work_dir, "deprecated", "SimpleFreeFieldTF_0.4.csv"))
    os.remove(os.path.join(
        work_dir, "deprecated", "SimpleFreeFieldTF_0.4.json"))

    # first run to test if conventions were updated
    sf.update_conventions(conventions_path=work_dir, assume_yes=True)
    out, _ = capfd.readouterr()
    assert "added convention: GeneralTF_2.0" in out
    assert "updated convention: GeneralFIR_1.0" in out
    assert "deprecated convention: MultiSpeakerBRIR_0.3" in out
    assert not os.path.isfile(
        os.path.join(work_dir, "MultiSpeakerBRIR_0.3.csv"))
    assert not os.path.isfile(
        os.path.join(work_dir, "MultiSpeakerBRIR_0.3.json"))
    assert "updated deprecated convention: SimpleFreeFieldHRIR_0.4" in out
    assert "added deprecated convention: SimpleFreeFieldTF_0.4" in out

    # second run to make sure that up to date conventions are not overwritten
    sf.update_conventions(conventions_path=work_dir, assume_yes=True)
    out, _ = capfd.readouterr()
    assert "added" not in out
    assert "updated" not in out
    assert "deprecated" not in out


def test__compile_conventions():
    """Test compiling the json conventions from the csv files."""

    # create temporary directory and copy existing source conventions
    temp_dir = TemporaryDirectory()
    shutil.copytree(
        os.path.join(os.path.dirname(__file__), "..", "sofar",
                     "sofa_conventions", "conventions"),
        os.path.join(temp_dir.name, "conventions"))

    # compile conventions
    _compile_conventions(os.path.join(temp_dir.name, "conventions"))

    # get list of reference json files
    paths_ref = _get_conventions("path")
    paths_test = _get_conventions(
        "path", os.path.join(temp_dir.name, "conventions"))

    for path_ref, path_test in zip(paths_ref, paths_test):

        # load reference conventions
        with open(path_ref, "r") as file:
            ref_data = json.load(file)

        with open(path_test, "r") as file:
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
    sofa_b.protected = False
    delattr(sofa_b, "ReceiverPosition")
    sofa_b.protected = True
    with pytest.warns(UserWarning, match="not identical: sofa_a has"):
        is_identical = sf.equals(sofa_a, sofa_b)
        assert not is_identical

    # check different keys
    sofa_b = deepcopy(sofa_a)
    sofa_b.protected = False
    sofa_b.PositionReceiver = sofa_b.ReceiverPosition
    delattr(sofa_b, "ReceiverPosition")
    sofa_b.protected = True
    with pytest.warns(UserWarning, match="not identical: sofa_a and sofa_b"):
        is_identical = sf.equals(sofa_a, sofa_b)
        assert not is_identical

    # check mismatching data types
    sofa_b = deepcopy(sofa_a)
    sofa_b.protected = False
    sofa_b._convention["ReceiverPosition"]["type"] = "int"
    sofa_b.protected = True
    with pytest.warns(UserWarning, match="not identical: ReceiverPosition"):
        is_identical = sf.equals(sofa_a, sofa_b)
        assert not is_identical

    # check exclude GLOBAL attributes
    sofa_b = deepcopy(sofa_a)
    sofa_b.protected = False
    delattr(sofa_b, "GLOBAL_Version")
    sofa_b.protected = True
    is_identical = sf.equals(sofa_a, sofa_b, exclude="GLOBAL")
    assert is_identical

    # check exclude Date attributes
    sofa_b = deepcopy(sofa_a)
    sofa_b.protected = False
    delattr(sofa_b, "GLOBAL_DateModified")
    sofa_b.protected = True
    is_identical = sf.equals(sofa_a, sofa_b, exclude="DATE")
    assert is_identical

    # check exclude Date attributes
    sofa_b = deepcopy(sofa_a)
    sofa_b.protected = False
    delattr(sofa_b, "GLOBAL_DateModified")
    sofa_b.protected = True
    is_identical = sf.equals(sofa_a, sofa_b, exclude="ATTR")
    assert is_identical


@pytest.mark.parametrize("value_a, value_b, attribute, fails", [
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
    sofa_a.protected = False
    sofa_b = deepcopy(sofa_a)

    # set parameters
    setattr(sofa_a, attribute, value_a)
    sofa_a.protected = True
    setattr(sofa_b, attribute, value_b)
    sofa_b.protected = True

    # compare
    if fails:
        with pytest.warns(UserWarning):
            assert not sf.equals(sofa_a, sofa_b)
    else:
        assert sf.equals(sofa_a, sofa_b)
