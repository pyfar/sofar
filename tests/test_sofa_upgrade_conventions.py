import sofar as sf
import os
import json

# load deprecation rules
base = os.path.join(
    os.path.dirname(__file__), "..", "sofar", "sofa_conventions", "rules")

with open(os.path.join(base, "upgrade.json"), "r") as file:
    upgrade = json.load(file)


def test_printouts_up_to_date(capfd):
    """Test console print for calling upgrade with up to date data"""

    sofa = sf.Sofa("SimpleFreeFieldHRIR")
    sofa.upgrade_convention()
    out, _ = capfd.readouterr()
    assert "is up to date" in out


def test_printouts(capfd):
    """Test console print for calling upgrade with deprecated data"""

    sofa = sf.Sofa("SimpleFreeFieldTF", verify=False)
    out, _ = capfd.readouterr()

    # calling with default arguments to get information only
    sofa.upgrade_convention()
    out, _ = capfd.readouterr()
    assert "can be upgraded" in out
    assert "SimpleFreeFieldHRTF v1.0" in out
    assert "invalud" not in out

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
