import pytest
from packaging import version
import re
import sofar as sf


# deprecate in 1.3.0 ----------------------------------------------------------
def test_pad_zero_modi():
    with pytest.warns(
            UserWarning,
            match=re.escape('Sofa.info() will be deprecated in sofar 1.3.0')):
        sofa = sf.Sofa('GeneralTF')
        sofa.info()

    if version.parse(sf.__version__) >= version.parse('1.3.0'):
        with pytest.raises(ValueError):
            # remove Sofa.info() from pyfar 1.3.0!
            sofa = sf.Sofa('GeneralTF')
            sofa.info()
