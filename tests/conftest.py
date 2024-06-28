import pytest
import numpy as np
import sofar as sf


# Temporary SOFA-file
@pytest.fixture
def temp_sofa_file(tmp_path_factory):
    """
    Temporary small SOFA file.
    To be used when data needs to be read from a SOFA file for testing.
    Contains custom data for "Data_IR", "GLOBAL_RoomType" and
    "Data_SamplingRate_Units".

    Returns
    -------
    filename : SOFA file
        Filename of temporary SOFA file
    """

    filename = tmp_path_factory.mktemp("data") / "test_sofastream.sofa"
    sofa = sf.Sofa("SimpleFreeFieldHRIR")
    sofa.Data_IR = np.array([[0, 1], [2, 3], [4, 5]])
    sofa.GLOBAL_RoomType = "free field"
    sofa.Data_SamplingRate_Units = "hertz"
    sf.write_sofa(filename, sofa)
    return filename
