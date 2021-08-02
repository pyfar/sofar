import sofar as sf
from pytest import raises


def test_get_convention():
    # test assertion for type of convention parameter
    with raises(TypeError, match="Convention must be a string"):
        sf.get_convention(1)
    # test assertion for invalid conventions
    with raises(ValueError, match="Convention 'invalid' not found"):
        sf.get_convention("invalid")
    with raises(ValueError, match="Found multiple matches"):
        sf.get_convention("Free")

    # test output
    convention = sf.get_convention("SimpleFreeFieldHRIR")
    assert isinstance(convention, dict)
