from sofar import SofaStream
import sofar as sf
from tempfile import TemporaryDirectory
from pytest import raises
import netCDF4
import numpy as np
import os

tempdir = TemporaryDirectory()
filename = os.path.join(tempdir.name, "test_sofastream.sofa")
sofa = sf.Sofa("SimpleFreeFieldHRIR")

sofa.Data_IR = np.array([[0, 1], [2, 3], [4, 5]])
sofa.GLOBAL_RoomType = "free field"
sofa.Data_SamplingRate_Units = "hertz"
sf.write_sofa(filename, sofa)

def test_sofastream_output():

    with SofaStream(filename) as file:
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
        np.testing.assert_array_equal(var_data.squeeze(), sofa.Data_IR)
        assert var_attr == 'hertz'
        # attribute values
        isinstance(att_data, str)
        assert att_data == sofa.GLOBAL_RoomType

def test_sofastream_warnings():

    with SofaStream(filename) as file:
        with raises(ValueError, match="attribute is not in dataset"):
            file.Wrong_Attribute

def test_sofastream_inspect(capfd):
    with SofaStream(filename) as file:
        file.inspect()
        out, _ = capfd.readouterr()
        assert "GLOBAL_SOFAConventions : SimpleFreeFieldHRIR" in out
        assert "Data_SamplingRate_Units : hertz" in out
        assert ("Data_IR : (M=3, R=2, N=1)\n"
                "  [[0. 1.]\n"
                "   [2. 3.]\n"
                "   [4. 5.]]") in out
