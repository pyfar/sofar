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


def test_printouts_deprecated(capfd):
    """Test console print for calling upgrade with deprecated data"""

    sofa = sf.Sofa("SimpleFreeFieldTF")
    out, _ = capfd.readouterr()

    # calling with default arguments to get information only
    sofa.upgrade_convention()
    out, _ = capfd.readouterr()
    assert "can be upgraded" in out
    assert "SimpleFreeFieldHRTF v1.0" in out
    assert "invalud" not in out

    # calling with valid target
    sofa.upgrade_convention("SimpleFreeFieldHRTF_1.0")
    out, _ = capfd.readouterr()
    assert "can be upgraded" not in out
    assert "invalid" not in out

    # calling with invalid target
    sofa.upgrade_convention("SimpleFreeFieldHRTF_0.1")
    out, _ = capfd.readouterr()
    assert "can be upgraded" in out
    assert "invalid" in out
    assert "SimpleFreeFieldHRTF v1.0" in out
