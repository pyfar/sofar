"""
Write rules for validating SOFA files to json files

Writes the following json files:
rules.json
    Rules for verifying SOFA conventions and files
unit_aliases.json
    Allowed aliases for the standard units

For a more detailed information about the json files referr to _readme.txt
"""
# %%
import json
import os
from sofar.utils import _get_conventions

# definition of valid coordinate systems. Not defined explicitly in AES69 but
# dozens of mentions of the following:
coords_min = ["cartesian", "spherical"]
coords_full = coords_min + ["spherical harmonics"]

# definition of units acordings to AES69-2020 Table 7
units_min = ["metre", "degree, degree, metre"]
units_full = units_min + [units_min[1]]

# allowed alternative versions of units
# NOTE: AES69 allows multi-unit strings to be seprated by comma, comma plus
#       space and space (AES69-2020 Section 4.7.8). This means that the unit
#       "cubic metre" will be tested as a multi unit string and is thus also
#       split in the aliases. A separate test for verifying that "cubic" is
#       followed be "metre" must be performed.
unit_aliases = {
    "metre": "metre",
    "metres": "metre",
    "meter": "metre",
    "meters": "metre",
    "cubic": "cubic",
    "degree": "degree",
    "degrees": "degree",
    "second": "second",
    "seconds": "second"
}
# possible values for restricted dimensions in the API
# Dimensions for spherical harmonics (considering orders up to 100) according
# to AES69-2020 Eq. (5) and (6)
sh_dimension = ([(N+1)**2 for N in range(100)],
                "(N+1)**2 where N is the spherical harmonics order")
# Dimensions for SOS (considering up to 100 sections) according to AES69-2020
# Appenx C.5.2
sos_dimension = ([6 * (N + 1) for N in range(100)],
                 "an integer multiple of 6 greater 0")

# verification rules
rules = {
    # Global --------------------------------------------------------------
    # Check value of GLOBAL_DataType (AES69-2020 Annex C)
    # (FIRE and TFE are legacy data types from SOFA version 1.0)
    "GLOBAL:DataType": {
        "value": ["FIR", "FIR-E", "FIRE", "TF", "TF-E", "TFE", "SOS"],
        "specific":  {
            "FIR": {
                "Data.IR": None,
                "Data.Delay": None,
                "Data.SamplingRate": None,
                "Data.SamplingRate:Units": ["hertz"]},
            "FIR-E": {
                "Data.IR": None,
                "Data.Delay": None,
                "Data.SamplingRate": None,
                "Data.SamplingRate:Units": ["hertz"]},
            "FIRE": {
                "Data.IR": None,
                "Data.Delay": None,
                "Data.SamplingRate": None,
                "Data.SamplingRate:Units": ["hertz"]},
            "TF": {
                "Data.Real": None,
                "Data.Imag": None,
                "N": None,
                "N:Units": ["hertz"]},
            "TF-E": {
                "Data.Real": None,
                "Data.Imag": None,
                "N": None,
                "N:Units": ["hertz"]},
            "TFE": {
                "Data.Real": None,
                "Data.Imag": None,
                "N": None,
                "N:Units": ["hertz"]},
            "SOS": {
                "Data.SOS": None,
                "Data.Delay": None,
                "Data.SamplingRate": None,
                "Data.SamplingRate:Units": ["hertz"],
                # Checking the dimension of N if having SOS data
                # (assuming up to 100 second order sections)
                "_dimensions": {
                    "N": {
                        "value": sos_dimension[0],
                        "value_str": sos_dimension[1]}
                }}}},
    # Specified in AES69-2020 SEction 4.7.7 and Table 6
    "GLOBAL:RoomType": {
        "value": ["free field", "reverberant", "shoebox", "dae"],
        "specific": {
            "reverberant": {
                "GLOBAL:RoomDescription": None},
            "shoebox": {
                "RoomCornerA": None,
                "RoomCornerB": None},
            "dae": {
                "GLOBAL:RoomGeometry": None}}},
    # Specified in AES69-2020 Annex D
    "GLOBAL:SOFAConventions": {
        "value": _get_conventions(return_type="name"),
        "specific": {
            "GeneralFIR": {
                "GLOBAL:DataType": ["FIR"]},
            "GeneralFIR-E": {
                "GLOBAL:DataType": ["FIR-E"]},
            "GeneralFIRE": {  # SOFA version 1.0 legacy
                "GLOBAL:DataType": ["FIRE"]},
            "GeneralTF": {
                "GLOBAL:DataType": ["TF"]},
            "GeneralTF-E": {
                "GLOBAL:DataType": ["TF-E"]},
            "SimpleFreeFieldHRIR": {
                "GLOBAL:DataType": ["FIR"],
                "GLOBAL:RoomType": ["free field"],
                "EmitterPosition:Type": coords_min,
                "_dimensions": {
                    "E": {
                        "value": [1],
                        "value_str": "1"}}},
            "SimpleFreeFieldHRTF": {
                "GLOBAL:DataType": ["TF"],
                "GLOBAL:RoomType": ["free field"],
                "EmitterPosition:Type": coords_min,
                "_dimensions": {
                    "E": {
                        "value": [1],
                        "value_str": "1"}}},
            "SimpleFreeFieldHRSOS": {
                "GLOBAL:DataType": ["SOS"],
                "GLOBAL:RoomType": ["free field"],
                "EmitterPosition:Type": coords_min,
                "_dimensions": {
                    "E": {
                        "value": [1],
                        "value_str": "1"}}},
            "FreeFieldHRIR": {
                "GLOBAL:DataType": ["FIR-E"],
                "GLOBAL:RoomType": ["free field"]},
            "FreeFieldHRTF": {
                "GLOBAL:DataType": ["TF-E"],
                "GLOBAL:RoomType": ["free field"]},
            "SimpleHeadphoneIR": {
                "GLOBAL:DataType": ["FIR"]},
            "SingleRoomSRIR": {
                "GLOBAL:DataType": ["FIR"]},
            "SingleRoomMIMOSRIR": {
                "GLOBAL:DataType": ["FIR-E"]},
            "FreeFieldDirectivityTF": {
                "GLOBAL:DataType": ["TF"]}}},
    # check NLongName (AES69-2020 Tables C.3 and C.4)
    "N:LongName": {
        "value": ["frequency"]},
    # Listener ------------------------------------------------------------
    # Possible values and dependencies are specified in
    # AES69-2020 Section 4.7.3
    # ---------------------------------------------------------------------
    # Check values and consistency of if ListenerPosition Type and Unit
    "ListenerPosition:Type": {
        "value": coords_min,
        "specific": {
            coords_min[0]: {
                "ListenerPosition:Units": [units_min[0]]},
            coords_min[1]: {
                "ListenerPosition:Units": [units_min[1]]}
        }},
    # Check if dependencies of ListenerView are contained
    "ListenerView": {
        "value": None,
        "general": ["ListenerView:Type", "ListenerView:Units"]},
    # Check values and consistency of if ListenerView Type and Unit
    "ListenerView:Type": {
        "value": coords_min,
        "specific": {
            coords_min[0]: {
                "ListenerView:Units": [units_min[0]]},
            coords_min[1]: {
                "ListenerView:Units": [units_min[1]]}
        }},
    # Check if dependencies of ListenerUp are contained
    "ListenerUp": {
        "value": None,
        "general": ["ListenerView"]},
    # Receiver ------------------------------------------------------------
    # Possible values and dependencies are specified in
    # AES69-2020 Section 4.7.4
    # ---------------------------------------------------------------------
    # Check values and consistency of if ReceiverPosition Type and Unit
    "ReceiverPosition:Type": {
        "value": coords_full,
        "specific": {
            coords_full[0]: {
                "ReceiverPosition:Units": [units_full[0]]},
            coords_full[1]: {
                "ReceiverPosition:Units": [units_full[1]]},
            coords_full[2]: {
                "ReceiverPosition:Units": [units_full[2]],
                "_dimensions": {
                    # Check dimension R if using spherical harmonics for the
                    # receiver (assuming SH orders < 100)
                    "R": {
                        "value": sh_dimension[0],
                        "value_str": sh_dimension[1]}}}
        }},
    # Check if dependencies of ReceiverView are contained
    "ReceiverView": {
        "value": None,
        "general": ["ReceiverView:Type", "ReceiverView:Units"]},
    # Check values and consistency of if ReceiverView Type and Unit
    "ReceiverView:Type": {
        "value": coords_min,
        "specific": {
            coords_min[0]: {
                "ReceiverView:Units": [units_min[0]]},
            coords_min[1]: {
                "ReceiverView:Units": [units_min[1]]}
            }},
    # Check if dependencies of ReceiverUp are contained
    "ReceiverUp": {
        "value": None,
        "general": ["ReceiverView"]},
    # Source --------------------------------------------------------------
    # Possible values and dependencies are specified in
    # AES69-2020 Section 4.7.5
    # ---------------------------------------------------------------------
    # Check values and consistency of if SourcePosition Type and Unit
    "SourcePosition:Type": {
        "value": coords_min,
        "specific": {
            coords_min[0]: {
                "SourcePosition:Units": [units_min[0]]},
            coords_min[1]: {
                "SourcePosition:Units": [units_min[1]]}
            }},
    # Check if dependencies of SourceView are contained
    "SourceView": {
        "value": None,
        "general": ["SourceView:Type", "SourceView:Units"]},
    # Check values and consistency of if SourceView Type and Unit
    "SourceView:Type": {
        "value": coords_min,
        "specific": {
            coords_min[0]: {
                "SourceView:Units": [units_min[0]]},
            coords_min[1]: {
                "SourceView:Units": [units_min[1]]}
            }},
    # Check if dependencies of SourceUp are contained
    "SourceUp": {
        "value": None,
        "general": ["SourceView"]},
    # Emitter -------------------------------------------------------------
    # Possible values and dependencies are specified in
    # AES69-2020 Section 4.7.6
    # ---------------------------------------------------------------------
    # Check values and consistency of if EmitterPosition Type and Unit
    "EmitterPosition:Type": {
        "value": coords_full,
        "specific": {
            coords_full[0]: {
                "EmitterPosition:Units": [units_full[0]]},
            coords_full[1]: {
                "EmitterPosition:Units": [units_full[1]]},
            coords_full[2]: {
                "EmitterPosition:Units": [units_full[2]],
                "_dimensions": {
                    # Check dimension R if using spherical harmonics for the
                    # receiver (assuming SH orders < 100)
                    "E": {
                        "value": sh_dimension[0],
                        "value_str": sh_dimension[1]}}}
        }},
    # Check if dependencies of EmitterView are contained
    "EmitterView": {
        "value": None,
        "general": ["EmitterView:Type", "EmitterView:Units"]},
    # Check values and consistency of if EmitterView Type and Unit
    "EmitterView:Type": {
        "value": coords_min,
        "specific": {
            coords_min[0]: {
                "EmitterView:Units": [units_min[0]]},
            coords_min[1]: {
                "EmitterView:Units": [units_min[1]]}
            }},
    # Check if dependencies of EmitterUp are contained
    "EmitterUp": {
        "value": None,
        "general": ["EmitterView"]},
    # Room ----------------------------------------------------------------
    # Possible values and dependencies are specified in
    # AES69-2020 Section 4.7.7
    # ---------------------------------------------------------------------
    "RoomVolume": {
        "value": None,
        "general": ["RoomVolume:Units"]},
    "RoomTemperature": {
        "value": None,
        "general": ["RoomTemperature:Units"]},
    "RoomVolume:Units": {
        "value": ["cubic metre"]},
    "RoomTemperature:Units": {
        "value": ["kelvin"]}
}

# deprecations
deprecations = {
    "GLOBAL:SOFAConventions": {
        "MusicalInstrumentDirectivityTF": "FreeFieldDirectivityTF",
        "SimpleFreeFieldDirectivityTF": "FreeFieldDirectivityTF",
        "SimpleBRIR": "MultiSpeakerBRIR",
        "SimpleFreeFieldTF": "SimpleFreeFieldHRTF",
        "SimpleFreeFieldSOS": "SimpleFreeFieldHRSOS",
        "SingleRoomDRIR": "SingleRoomSRIR"
    }
}

# write to json files
for content, name in zip([rules, unit_aliases, deprecations],
                         ["rules", "unit_aliases", "deprecations"]):

    json_file = os.path.join(os.path.dirname(__file__), name + '.json')
    with open(json_file, 'w') as file:
        json.dump(content, file, indent=4)
