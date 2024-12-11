from sofar import SofaStream
from tempfile import TemporaryDirectory
import pytest
import netCDF4
import numpy as np
import os
import sofar as sf


def test_sofastream_output(temp_sofa_file):

    with SofaStream(temp_sofa_file) as file:
        obj = file
        var = file.Data_IR
        var_data = var[:]
        var_attr = file.Data_SamplingRate_Units
        att_data = file.GLOBAL_RoomType

        # check SofaStream instance
        isinstance(obj, SofaStream)
        # check returned variable type
        isinstance(var, netCDF4._netCDF4.Variable)
        # variable values
        isinstance(var_data, np.ma.core.MaskedArray)
        np.testing.assert_array_equal(var_data.squeeze(),
                                      np.array([[0, 1], [2, 3], [4, 5]]))
        assert var_attr == 'hertz'
        # attribute values
        isinstance(att_data, str)
        assert att_data == "free field"


def test_sofastream_attribute_error(temp_sofa_file):

    with SofaStream(temp_sofa_file) as file:
        with pytest.raises(
                AttributeError,
                match="Wrong_Attribute is not contained in SOFA-file"):
            file.Wrong_Attribute    # noqa: B018


def test_sofastream_inspect(capfd, temp_sofa_file):

    tempdir = TemporaryDirectory()
    inspect_file = os.path.join(tempdir.name, "info.txt")

    with SofaStream(temp_sofa_file) as file:
        file.inspect(inspect_file)
        out, _ = capfd.readouterr()

    sofa = sf.read_sofa(temp_sofa_file)
    sofa.inspect()
    out_sofa, _ = capfd.readouterr()

    assert out_sofa == out

    # check text file
    with open(inspect_file, "r") as out_inspect:
        text = out_inspect.readlines()
    assert out == "".join(text)


def test_list_dimensions(capfd, tmp_path_factory):

    filename = tmp_path_factory.mktemp("data") / "test_sofastream_dim.sofa"

    # test FIR Data
    sofa = sf.Sofa("GeneralFIR")
    sf.write_sofa(filename, sofa)
    with SofaStream(filename) as file:
        file.list_dimensions    # noqa: B018
        out, _ = capfd.readouterr()
        assert "N = 1 samples" in out

    # test TF Data
    sofa = sf.Sofa("GeneralTF")
    sf.write_sofa(filename, sofa)
    with SofaStream(filename) as file:
        file.list_dimensions    # noqa: B018
        out, _ = capfd.readouterr()
        assert "N = 1 frequencies" in out

    # test SOS Data
    sofa = sf.Sofa("SimpleFreeFieldHRSOS")
    sf.write_sofa(filename, sofa)
    with SofaStream(filename) as file:
        file.list_dimensions    # noqa: B018
        out, _ = capfd.readouterr()
        assert "N = 6 SOS coefficients" in out

    # test non spherical harmonics data
    sofa = sf.Sofa("GeneralFIR")
    sf.write_sofa(filename, sofa)
    with SofaStream(filename) as file:
        file.list_dimensions    # noqa: B018
        out, _ = capfd.readouterr()
        assert "E = 1 emitter" in out
        assert "R = 1 receiver" in out

    # test spherical harmonics data
    sofa.EmitterPosition_Type = "spherical harmonics"
    sofa.ReceiverPosition_Type = "spherical harmonics"
    sofa.EmitterPosition_Units = "degree, degree, metre"
    sofa.ReceiverPosition_Units = "degree, degree, metre"
    sf.write_sofa(filename, sofa)
    with SofaStream(filename) as file:
        file.list_dimensions  # noqa: B018
        out, _ = capfd.readouterr()
    assert "E = 1 emitter spherical harmonics coefficients" in out
    assert "R = 1 receiver spherical harmonics coefficients" in out


def test_get_dimensions(tmp_path_factory):
    """Test getting the size of dimensions."""
    filename = tmp_path_factory.mktemp("data") / "test_sofastream_dim.sofa"

    # test FIR Data
    sofa = sf.Sofa("GeneralFIR")
    sf.write_sofa(filename, sofa)

    with SofaStream(filename) as file:
        size = file.get_dimension('N')
        assert size == 1

        # test wrong dimension error
        with pytest.raises(ValueError, match="Q is not a valid dimension"):
            file.get_dimension("Q")
