"""
Write rules for validating SOFA files to json files

Writes the following json files:
data.json
    General restrictions on the data of any SOFA convention
data_type.json
    Restriction depending on GLOBAL_DataType
api.json
    Restrictions on the API depending on specific fields of a SOFA file
convention.json
    Restrictions for specific conventions
unit_aliases.json
    Allowed aliases for the standard units

For a more detailed information about the json files referr to _readme.txt
"""

import json
import os
from sofar.sofar import _get_conventions

# definition of valid coordinate systems and units
coords_min = ["cartesian", "spherical"]
coords_full = coords_min + ["spherical harmonics"]
units_min = ["metre", "degree, degree, metre"]
units_full = units_min + [units_min[1]]
unit_aliases = {
    "metres": "metre",
    "meter": "metre",
    "meters": "metre",
    "cubic metres": "cubic metre",
    "cubic meter": "cubic metre",
    "cubic meters": "cubic metre",
    "degrees": "degree",
    "seconds": "second"
}
# possible values for restricted dimensions in the API
sh_dimension = ([(N+1)**2 for N in range(200)],
                "(N+1)**2 where N is the spherical harmonics order")
sos_dimension = ([6 * (N + 1) for N in range(1000)],
                 "an integer multiple of 6 greater 0")

# restrictions on the data
# - if `value` is None it in only checked if the SOFA object has the attr
# - if `value` is a list, it is also checked if the actual value is in
#   `value`
# - if there is a list of values for a dependency the value of the SOFA
#   object has to match the value of the list at a certain index. The index
#   is determined by the value of the parent.
data = {
    # Global --------------------------------------------------------------
    # GLOBAL_SOFAConventions?
    # Check value of GLOBAL_DataType
    # (FIRE and TFE are legacy data types from SOFA version 1.0)
    "GLOBAL_DataType": {
        "value": ["FIR", "FIR-E", "FIRE", "TF", "TF-E", "TFE", "SOS"]},
    "GLOBAL_RoomType": {
        "value": ["free field", "reverberant", "shoebox", "dae"]},
    "GLOBAL_SOFAConventions": {
        "value": _get_conventions(return_type="name")},
    # check NLongName
    "N_LongName": {
        "value": ["frequency"]},
    # Listener ------------------------------------------------------------
    # Check values and consistency of if ListenerPosition Type and Unit
    "ListenerPosition_Type": {
        "value": coords_min,
        "dependency": {
            "ListenerPosition_Units": units_min}},
    # Check if dependencies of ListenerView are contained
    "ListenerView": {
        "value": None,
        "dependency": {
            "ListenerView_Type": None,
            "ListenerView_Units": None}},
    # Check values and consistency of if ListenerView Type and Unit
    "ListenerView_Type": {
        "value": coords_min,
        "dependency": {
            "ListenerView_Units": units_min}},
    # Check if dependencies of ListenerUp are contained
    "ListenerUp": {
        "value": None,
        "dependency": {
            "ListenerView": None}},
    # Receiver ------------------------------------------------------------
    # Check values and consistency of if ReceiverPosition Type and Unit
    "ReceiverPosition_Type": {
        "value": coords_full,
        "dependency": {
            "ReceiverPosition_Units": units_full}},
    # Check if dependencies of ReceiverView are contained
    "ReceiverView": {
        "value": None,
        "dependency": {
            "ReceiverView_Type": None,
            "ReceiverView_Units": None}},
    # Check values and consistency of if ReceiverView Type and Unit
    "ReceiverView_Type": {
        "value": coords_min,
        "dependency": {
            "ReceiverView_Units": units_min}},
    # Check if dependencies of ReceiverUp are contained
    "ReceiverUp": {
        "value": None,
        "dependency": {
            "ReceiverView": None}},
    # Source --------------------------------------------------------------
    # Check values and consistency of if SourcePosition Type and Unit
    "SourcePosition_Type": {
        "value": coords_min,
        "dependency": {
            "SourcePosition_Units": units_min}},
    # Check if dependencies of SourceView are contained
    "SourceView": {
        "value": None,
        "dependency": {
            "SourceView_Type": None,
            "SourceView_Units": None}},
    # Check values and consistency of if SourceView Type and Unit
    "SourceView_Type": {
        "value": coords_min,
        "dependency": {
            "SourceView_Units": units_min}},
    # Check if dependencies of SourceUp are contained
    "SourceUp": {
        "value": None,
        "dependency": {
            "SourceView": None}},
    # Emitter -------------------------------------------------------------
    # Check values and consistency of if EmitterPosition Type and Unit
    "EmitterPosition_Type": {
        "value": coords_full,
        "dependency": {
            "EmitterPosition_Units": units_full}},
    # Check if dependencies of EmitterView are contained
    "EmitterView": {
        "value": None,
        "dependency": {
            "EmitterView_Type": None,
            "EmitterView_Units": None}},
    # Check values and consistency of if EmitterView Type and Unit
    "EmitterView_Type": {
        "value": coords_min,
        "dependency": {
            "EmitterView_Units": units_min}},
    # Check if dependencies of EmitterUp are contained
    "EmitterUp": {
        "value": None,
        "dependency": {
            "EmitterView": None}},
    # Room ----------------------------------------------------------------
    "RoomVolume": {
        "value": None,
        "dependency": {
            "RoomVolume_Units": None}},
    "RoomTemperature": {
        "value": None,
        "dependency": {
            "RoomTemperature_Units": None}},
    "RoomVolume_Units": {
        "value": ["cubic metre"]},
    "RoomTemperature_Units": {
        "value": ["kelvin"]}
}

# restrictions arising from GLOBAL_DataType
# - if `value` is None it is only checked if the SOFA object has the attr
# - if `value` is a list, it is also checked if the actual value is in
#   `value`
data_type = {
    "FIR": {
        "Data_IR": None,
        "Data_Delay": None,
        "Data_SamplingRate": None,
        "Data_SamplingRate_Units": "hertz"},
    "TF": {
        "Data_Real": None,
        "Data_Imag": None,
        "N": None,
        # "N_LongName": (["frequency"], "frequency"),  # optional parameter
        "N_Units": "hertz"},
    "SOS": {
        "Data_SOS": None,
        "Data_Delay": None,
        "Data_SamplingRate": None,
        "Data_SamplingRate_Units": "hertz"}
}

# restrictions on the API
api = {
    # Check dimension R if using spherical harmonics for the Receiver
    # (assuming SH orders < 200)
    "ReceiverPosition_Type": {
        "value": "spherical harmonics",
        "API": ("R", ) + sh_dimension},
    # Check dimension E if using spherical harmonics for the Emitter
    # (assuming SH orders < 200)
    "EmitterPosition_Type": {
        "value": "spherical harmonics",
        "API": ("E", ) + sh_dimension},
    # Checking the dimension of N if having SOS data
    # (assuming up to 1000 second order sections)
    "GLOBAL_DataType": {
        "value": "SOS",
        "API": ("N", ) + sos_dimension}
}

# restrictions from the convention. Values of fields will be checked.
# Must contain testing the API. If this would be tested under api={}, the
# entry GLOBAL_SOFAConventions would be repeated.
convention = {
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
        "API": {"E": 1}},
    "SimpleFreeFieldHRTF": {
        "GLOBAL_DataType": ["TF"],
        "GLOBAL_RoomType": ["free field"],
        "EmitterPosition_Type": coords_min,
        "API": {"E": 1}},
    "SimpleFreeFieldHRSOS": {
        "GLOBAL_DataType": ["SOS"],
        "GLOBAL_RoomType": ["free field"],
        "EmitterPosition_Type": coords_min,
        "API": {"E": 1}},
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
        "GLOBAL_DataType": ["TF"]}
}

# write to json files
for rules, name in zip(
        [data, data_type, api, convention, unit_aliases],
        ["data", "data_type", "api", "convention", "unit_aliases"]):

    json_file = os.path.join(os.path.dirname(__file__), name + '.json')
    with open(json_file, 'w') as file:
        json.dump(rules, file, indent=4)
