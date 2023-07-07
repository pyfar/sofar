import sofar as sf
from sofar.utils import _get_conventions
import pytest
import os
import json

# load deprecation rules
base = os.path.join(
    os.path.dirname(__file__), "..", "sofar", "sofa_conventions", "rules")

with open(os.path.join(base, "upgrade.json"), "r") as file:
    upgrade = json.load(file)

# load convention paths
paths = _get_conventions("paths")


def test_printouts(capfd):
    """
    Test console print for calling upgrade with up to data and deprecated data
    """

    # test printouts with up to data convention -------------------------------
    sofa = sf.Sofa("SimpleFreeFieldHRIR")
    sofa.upgrade_convention()
    out, _ = capfd.readouterr()
    assert "is up to date" in out

    # test printouts with outdated conventions --------------------------------
    sofa = sf.Sofa("SimpleFreeFieldTF", verify=False)
    out, _ = capfd.readouterr()

    # calling with default arguments to get information only
    sofa.upgrade_convention()
    out, _ = capfd.readouterr()
    assert "can be upgraded" in out
    assert "SimpleFreeFieldHRTF v1.0" in out
    assert "invalid" not in out

    # calling with invalid target
    sofa.upgrade_convention("SimpleFreeFieldHRTF_0.1")
    out, _ = capfd.readouterr()
    assert "can be upgraded" in out
    assert "invalid" in out
    assert "SimpleFreeFieldHRTF v1.0" in out

    # calling with valid target (nothing to move, remove, no message)
    sofa.upgrade_convention("SimpleFreeFieldHRTF_1.0")
    out, _ = capfd.readouterr()
    assert "can be upgraded" not in out
    assert "invalid" not in out
    assert "Upgrading SimpleFreeFieldTF v1.0" in out
    assert "to SimpleFreeFieldHRTF v1.0" in out
    assert "No data to move" in out
    assert "No data to remove" in out
    assert "All mandatory data contained" in out

    # calling with valid target (including message)
    sofa = sf.Sofa("SimpleFreeFieldHRIR", version="0.4", verify=False)
    out, _ = capfd.readouterr()
    sofa.upgrade_convention("SimpleFreeFieldHRIR_1.0")
    out, _ = capfd.readouterr()
    assert "Consider to add the optional data 'SourceUp'" in out

    # calling with valid target (things to move)
    sofa = sf.Sofa("MultiSpeakerBRIR", verify=False)
    out, _ = capfd.readouterr()
    sofa.upgrade_convention("SingleRoomMIMOSRIR_1.0")
    out, _ = capfd.readouterr()
    assert "Moving Data_IR" in out


@pytest.mark.parametrize("path", paths)
def test_upgrade_conventions(path, capfd):

    # extract information for testing
    convention, version = os.path.basename(path).split("_")
    version = version[:-5]
    deprecated = "deprecated" in path

    # get SOFA object and targets for upgrading
    sofa = sf.Sofa(convention, version=version, verify=False)
    out, _ = capfd.readouterr()
    targets = sofa.upgrade_convention()
    out, _ = capfd.readouterr()

    # don't verify conventions that might require user action after
    if os.path.basename(path) in ["FreeFieldDirectivityTF_1.0.json"]:
        # FreeFieldDirectivityTF_1.0
        # - optional dependency GLOBAL_EmitterDescription
        #   might need to be added
        verify = False
    else:
        verify = True

    if targets:
        for target in targets:
            sofa.upgrade_convention(target, verify=verify)
            out, _ = capfd.readouterr()
            assert "Upgrading" in out
    else:
        assert not deprecated
