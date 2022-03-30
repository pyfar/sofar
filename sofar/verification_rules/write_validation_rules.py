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
    "GLOBAL_DataType": {
        "value": ["FIR", "FIR-E", "FIRE", "TF", "TF-E", "TFE", "SOS"],
        "specific":  {
            "FIR": {
                "Data_IR": None,
                "Data_Delay": None,
                "Data_SamplingRate": None,
                "Data_SamplingRate_Units": ["hertz"]},
            "FIR-E": {
                "Data_IR": None,
                "Data_Delay": None,
                "Data_SamplingRate": None,
                "Data_SamplingRate_Units": ["hertz"]},
            "FIRE": {
                "Data_IR": None,
                "Data_Delay": None,
                "Data_SamplingRate": None,
                "Data_SamplingRate_Units": ["hertz"]},
            "TF": {
                "Data_Real": None,
                "Data_Imag": None,
                "N": None,
                "N_Units": ["hertz"]},
            "TF-E": {
                "Data_Real": None,
                "Data_Imag": None,
                "N": None,
                "N_Units": ["hertz"]},
            "TFE": {
                "Data_Real": None,
                "Data_Imag": None,
                "N": None,
                "N_Units": ["hertz"]},
            "SOS": {
                "Data_SOS": None,
                "Data_Delay": None,
                "Data_SamplingRate": None,
                "Data_SamplingRate_Units": ["hertz"],
                # Checking the dimension of N if having SOS data
                # (assuming up to 100 second order sections)
                "_dimensions": {
                    "N": {
                        "value": sos_dimension[0],
                        "value_str": sos_dimension[1]}
                }}}},
    # Specified in AES69-2020 SEction 4.7.7 and Table 6
    "GLOBAL_RoomType": {
        "value": ["free field", "reverberant", "shoebox", "dae"],
        "specific": {
            "reverberant": {
                "GLOBAL_RoomDescription": None},
            "shoebox": {
                "RoomCornerA": None,
                "RoomCornerB": None},
            "dae": {
                "GLOBAL_RoomGeometry": None}}},
    # Specified in AES69-2020 Annex D
    "GLOBAL_SOFAConventions": {
        "value": _get_conventions(return_type="name"),
        "specific": {
            "GeneralFIR": {
                "GLOBAL_DataType": ["FIR"]},
            "GeneralFIR-E": {
                "GLOBAL_DataType": ["FIR-E"]},
            "GeneralFIRE": {  # SOFA version 1.0 legacy
                "GLOBAL_DataType": ["FIRE"]},
            "GeneralTF": {
                "GLOBAL_DataType": ["TF"]},
            "GeneralTF-E": {
                "GLOBAL_DataType": ["TF-E"]},
            "SimpleFreeFieldHRIR": {
                "GLOBAL_DataType": ["FIR"],
                "GLOBAL_RoomType": ["free field"],
                "EmitterPosition_Type": coords_min,
                "_dimensions": {
                    "E": {
                        "value": [1],
                        "value_str": "1"}}},
            "SimpleFreeFieldHRTF": {
                "GLOBAL_DataType": ["TF"],
                "GLOBAL_RoomType": ["free field"],
                "EmitterPosition_Type": coords_min,
                "_dimensions": {
                    "E": {
                        "value": [1],
                        "value_str": "1"}}},
            "SimpleFreeFieldHRSOS": {
                "GLOBAL_DataType": ["SOS"],
                "GLOBAL_RoomType": ["free field"],
                "EmitterPosition_Type": coords_min,
                "_dimensions": {
                    "E": {
                        "value": [1],
                        "value_str": "1"}}},
            "FreeFieldHRIR": {
                "GLOBAL_DataType": ["FIR-E"],
                "GLOBAL_RoomType": ["free field"]},
            "FreeFieldHRTF": {
                "GLOBAL_DataType": ["TF-E"],
                "GLOBAL_RoomType": ["free field"]},
            "SimpleHeadphoneIR": {
                "GLOBAL_DataType": ["FIR"]},
            "SingleRoomSRIR": {
                "GLOBAL_DataType": ["FIR"]},
            "SingleRoomMIMOSRIR": {
                "GLOBAL_DataType": ["FIR-E"]},
            "FreeFieldDirectivityTF": {
                "GLOBAL_DataType": ["TF"]}}},
    # check NLongName (AES69-2020 Tables C.3 and C.4)
    "N_LongName": {
        "value": ["frequency"]},
    # Listener ------------------------------------------------------------
    # Possible values and dependencies are specified in
    # AES69-2020 Section 4.7.3
    # ---------------------------------------------------------------------
    # Check values and consistency of if ListenerPosition Type and Unit
    "ListenerPosition_Type": {
        "value": coords_min,
        "specific": {
            coords_min[0]: {
                "ListenerPosition_Units": [units_min[0]]},
            coords_min[1]: {
                "ListenerPosition_Units": [units_min[1]]}
        }},
    # Check if dependencies of ListenerView are contained
    "ListenerView": {
        "value": None,
        "general": ["ListenerView_Type", "ListenerView_Units"]},
    # Check values and consistency of if ListenerView Type and Unit
    "ListenerView_Type": {
        "value": coords_min,
        "specific": {
            coords_min[0]: {
                "ListenerView_Units": [units_min[0]]},
            coords_min[1]: {
                "ListenerView_Units": [units_min[1]]}
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
    "ReceiverPosition_Type": {
        "value": coords_full,
        "specific": {
            coords_full[0]: {
                "ReceiverPosition_Units": [units_full[0]]},
            coords_full[1]: {
                "ReceiverPosition_Units": [units_full[1]]},
            coords_full[2]: {
                "ReceiverPosition_Units": [units_full[2]],
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
        "general": ["ReceiverView_Type", "ReceiverView_Units"]},
    # Check values and consistency of if ReceiverView Type and Unit
    "ReceiverView_Type": {
        "value": coords_min,
        "specific": {
            coords_min[0]: {
                "ReceiverView_Units": [units_min[0]]},
            coords_min[1]: {
                "ReceiverView_Units": [units_min[1]]}
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
    "SourcePosition_Type": {
        "value": coords_min,
        "specific": {
            coords_min[0]: {
                "SourcePosition_Units": [units_min[0]]},
            coords_min[1]: {
                "SourcePosition_Units": [units_min[1]]}
            }},
    # Check if dependencies of SourceView are contained
    "SourceView": {
        "value": None,
        "general": ["SourceView_Type", "SourceView_Units"]},
    # Check values and consistency of if SourceView Type and Unit
    "SourceView_Type": {
        "value": coords_min,
        "specific": {
            coords_min[0]: {
                "SourceView_Units": [units_min[0]]},
            coords_min[1]: {
                "SourceView_Units": [units_min[1]]}
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
    "EmitterPosition_Type": {
        "value": coords_full,
        "specific": {
            coords_full[0]: {
                "EmitterPosition_Units": [units_full[0]]},
            coords_full[1]: {
                "EmitterPosition_Units": [units_full[1]]},
            coords_full[2]: {
                "EmitterPosition_Units": [units_full[2]],
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
        "general": ["EmitterView_Type", "EmitterView_Units"]},
    # Check values and consistency of if EmitterView Type and Unit
    "EmitterView_Type": {
        "value": coords_min,
        "specific": {
            coords_min[0]: {
                "EmitterView_Units": [units_min[0]]},
            coords_min[1]: {
                "EmitterView_Units": [units_min[1]]}
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
        "general": ["RoomVolume_Units"]},
    "RoomTemperature": {
        "value": None,
        "general": ["RoomTemperature_Units"]},
    "RoomVolume_Units": {
        "value": ["cubic metre"]},
    "RoomTemperature_Units": {
        "value": ["kelvin"]}
}

# write to json files
for content, name in zip([rules, unit_aliases], ["rules", "unit_aliases"]):

    json_file = os.path.join(os.path.dirname(__file__), name + '.json')
    with open(json_file, 'w') as file:
        json.dump(content, file, indent=4)
