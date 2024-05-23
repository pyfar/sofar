from sofar import SofaStream
import sofar as sf
from tempfile import TemporaryDirectory
from pytest import raises
import pytest
import netCDF4
import numpy as np
import os

# Temporary SOFA-file
@pytest.fixture
def temp_sofa_file(tmp_path_factory):

    filename = tmp_path_factory.mktemp("data") / "test_sofastream.sofa"
    sofa = sf.Sofa("SimpleFreeFieldHRIR")
    sofa.Data_IR = np.array([[0, 1], [2, 3], [4, 5]])
    sofa.GLOBAL_RoomType = "free field"
    sofa.Data_SamplingRate_Units = "hertz"
    sf.write_sofa(filename, sofa)
    return filename

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

def test_sofastream_warnings(temp_sofa_file):

    with SofaStream(temp_sofa_file) as file:
        with raises(ValueError, match="attribute is not in dataset"):
            file.Wrong_Attribute

def test_sofastream_inspect(capfd, temp_sofa_file):

    tempdir = TemporaryDirectory()
    inspect_file = os.path.join(tempdir.name, "info.txt")

    with SofaStream(temp_sofa_file) as file:
        file.inspect(inspect_file)
        out, _ = capfd.readouterr()
        assert "GLOBAL_SOFAConventions : SimpleFreeFieldHRIR" in out
        assert "Data_SamplingRate_Units : hertz" in out
        assert ("Data_IR : (M=3, R=2, N=1)\n"
                "  [[0. 1.]\n"
                "   [2. 3.]\n"
                "   [4. 5.]]") in out

    # check text file
    with open(inspect_file, "r") as out_inspect:
        text = out_inspect.readlines()
    assert out == "".join(text)
