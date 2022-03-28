The following details how SOFA files must be validated to follow the SOFA
standard AES69-2020. The validation rules make use of the SOFA conventions
contained in the folder ../conventions and the json files contained in this
folder and explained below.

1. Mandatory variables and attributes must be contained in the file. Such data
   has the flag "m" in the conventions.
2. All data must have the correct type (double, string, attribute) as denoted
   the field "type" in the conventions.
3. All variables must have the correct dimensions as denoted by the
   "dimemsions" in the conventions. The dimensions is determined from the
   variable that lists it with a lower case letter. E.g. if Data_IR shall have
   the dimension "mrn" the and the actual shape of Data_IR is (10, 2, 128),
   then M=10, R=2, and N=128.
4. Variable and attribute names must not start with an underscore
5. SOFA is case insensitive when checking the values of attributes with the
   following exception.
6. Units, i.e., all attributes that end with "Units" shall contain only lower
   case letters when writing but may contain upper case characters when Reading
   data.
7. Different spelling of the units are allowed (see unit_aliases.json)
8. Strings containing multiple units can be separated by commas, commas and
   spaces, or spaces, e.g., "meter,meter,meter", "meter, meter, meter",
   "meter meter meter", or mixtures thereof
9. All validation rules from rules.json must be checked (see below)

The json files inside this folder contain rules for validating SOFA files.
The rules were manually extracted from the SOFA Standard AES69-2020 and are
distributed across five files


data.json
---------

Contains all validation rules
- that can not be derived from the SOFA conventions
- that do not pertain to units and unit strings

Note that the values of units MUST always be given in reference units as
detailed for unit_aliases.json (see below)

The rules are contained in a json file with the following structure
(explanation below, examples refer to rules.json)

{
   key_1: {
      "value": values
      "general": [sub_key_1, sub_key_2, ..., sub_key_N],
      "specific": {
         value_1: {
            sub_key_1: values
            .
            .
            .
            sub_key_N: values
            "_dimensions": {
               dimension_1: {
                  "value": values,
                  "value_str": value_string
               },
               .
               .
               .
               dimensions_N: {...}
            }
         }
         value_2: {...},
         .
         .
         .
         value_N: {...}
      }
   },
   key_2: {...},
   .
   .
   .
   key_N: {...}
}

KEYS
----

`key_1`, `key_2`, ... `key_N` are the names of SOFA variables (e.g.,
'ReceiverPosition') or attributes (e.g., 'GLOBAL_DataType').

VALUES
------

`values` are either a list of possible values that a variable of attribute must
have or null, if the variable or attribute can have any value.
EXAMPLE: 'GLOBAL_DataType' (`key`) can be ["FIR", "FIR-E", "FIRE" "TF", "TF-E",
         "TFE", "SOS"] (`value`) and an error should be raised if
         'GLOBAL_DataType' has any other value. If `values` was null,
         'GLOBAL_DataType' could have any value.

DEPENDENCIES
------------

A variable or attribute (`key`) can have two different kinds of dependencies.
general" and "specific". If there are such dependencies, a `key` is
followed by the corresponding fields.
EXAMPLE: 'GLOBAL_DataType' (`key`) has "specific" dependencies and
         'ListenerPosition_Type' (`key`) has "general" dependencies.

GENERAL DEPENDENCIES
--------------------

General dependencies are simple. The contain an list that contains an arbitrary
number of variables and attributes (`sub_keys`), which must be contained in a
SOFA object IF `key` is contained.
EXAMPLE: 'ListenerView_Type' must be contained if 'ListenerView' is contained.

SPECIFIC DEPENDENCIES
---------------------

Specific dependencies are more complex. They describe dependencies for a
variable or attribute (`sub_key_1`, `sub_key_2`, ..., `sub_key_N`) that only
have to be enforced if `key` has a specific value (`value_1`, `value_2`, ...
, `value_N`). There are three possible dependencies.

1. If the value of `sub_key` is null, it only has to be checked if `sub_key` is
   contained in the Sofa object
   EXAMPLE: If 'GLOBAL_DataType' is "FIR", 'Data_IR' must be contained
2. If the value is not null, `sub_key` must have on of the listed values.
   EXAMPLE: If 'GLOBAL_DataType' is "FIR", 'Data_SamplingRate_Units' must be
            "hertz"
3. If the `sub_key` is "_dimensions", the size of on or more SOFA/NetCDF
   dimensions is restricted to one or more certain values.
   EXAMPLE: If 'GLOBAL_DataType' is "SOS", the dimension 'N' must be an integer
            multiple of 6 (in this specific case provided as a list of
            possible values up to 600).
   For restrictions on the dimensions the rules also provide a verbose error
   message that can be used for feedback in case the dependency is violated.
   EXAMPLE: The error message for the case described above is "an integer
            multiple of 6 greater 0"



unit_aliases.json
-----------------
Contains a list of possible variants of unit names. The structure is as follows

{
   variant_1_unit_1: reference_unit_1
   variant_2_unit_1: reference_unit_2
   .
   .
   .
   variant_N_unit_1: reference_unit_1
   variant_1_unit_2: reference_unit_2
   .
   .
   .
   variant_N_unit_N: reference_unit_N
}

EXAMPLE: The unit "metre" (`reference_unit_1`) can also be written "metres",
         "meter", and "meters" (`variant_1_unit_1`, `variant_2_unit_1`,
         `variant_3_unit_1`).
