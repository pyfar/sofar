import sofar as sf
import os
from pytest import raises


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

    # set with key as string
    sf.set_value(convention, "ListenerPosition", [0, 0, 1])
    assert convention["ListenerPosition"] == [0, 0, 1]

    # set with key as list
    sf.set_value(convention, ["Data", "IR"], [0, 0, 1])
    assert convention["Data"]["IR"] == [0, 0, 1]

    # set with invalid key (key does not exist)
    with raises(ValueError, match="The attribute"):
        sf.set_value(convention, ["Data.IR"], [0, 0, 1])
    # set with invalid key (key is nested dictionary)
    with raises(ValueError, match="The attribute"):
        sf.set_value(convention, "Data", [0, 0, 1])
