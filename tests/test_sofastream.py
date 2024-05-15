from sofar import Sofastream
import pytest
from pytest import raises
import netCDF4
import numpy as np
import os


def test_sofastream_output():
    filename = os.path.join(os.getcwd(), 'tests', 'test_io_data',
                    'FABIAN_HRIR_measured_HATO_0.sofa')

    with Sofastream(filename) as file:
        obj = file
        var = file.Data_IR
        var_data = var[:]
        att_data = file.GLOBAL_RoomType

        # check Sofastream instance
        isinstance(obj, Sofastream)
        # check returned variable type
        isinstance(var, netCDF4._netCDF4.Variable)
        # variable values
        isinstance(var_data, np.ma.core.MaskedArray)
        assert var_data.shape == (11950, 2, 256)
        # attribute values
        isinstance(att_data, str)
        assert att_data == "free field"

def test_sofastream_warnings():
    filename = os.path.join(os.getcwd(), 'tests', 'test_io_data',
                    'FABIAN_HRIR_measured_HATO_0.sofa')

    with Sofastream(filename) as file:
        with raises(ValueError, match="attribute is not in dataset"):
            file.Wrong_Attribute
