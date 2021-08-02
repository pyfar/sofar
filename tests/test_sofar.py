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


def test_get_convention():
    # test assertion for type of convention parameter
    with raises(TypeError, match="Convention must be a string"):
        sf.get_convention(1)
    # test assertion for invalid conventions
    with raises(ValueError, match="Convention 'invalid' not found"):
        sf.get_convention("invalid")

    # test output
    paths = sf.list_conventions(print_conventions=False, return_paths=True)
    for path in paths:
        name = os.path.basename(path).split(sep="_")[0]
        print(f"Testing: {name}")
        convention = sf.get_convention(name)
        assert isinstance(convention, dict)
