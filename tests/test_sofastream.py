from sofar import SofaStream
from tempfile import TemporaryDirectory
from pytest import raises
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
        with raises(AttributeError,
                    match="Wrong_Attribute is not contained in SOFA-file"):
            file.Wrong_Attribute


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
