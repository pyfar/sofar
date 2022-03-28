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
4. SOFA is case insensitive when checking the values of attributes with the
   following exception.
5. Units, i.e., all attributes that end with "Units" shall contain only lower
   case letters when writing but may contain upper case characters when Reading
   data.
6. Different spelling of the units are allowed (see unit_aliases.json)
7. All validation rules for the used convention must be checked (see
   convention.json)
8. All validation rules for the used DataType must be checked (see
   data_type.json)
9. All validation rules for specific variables and attributes must be checked
   (see data.json and api.json)

The json files inside this folder contain rules for validating SOFA files.
The rules were manually extracted from the SOFA Standard AES69-2020 and are
distributed across five files


api.json
--------

Validation rules to verify restrictions on the API (Dimensions of the
underlying NetCDF file) depending on specific attributes. The file contains a
list of attributes, the value that an attribute must have to trigger the
verification, as well as the name of the affected dimension along possible
values and a verbose error message that can be used if the verification failed.

For example, if the `RecieverPosition_Type` is "spherical harmonics", the
dimension "R" must equal (N+1)**2 with N = 0, 1, 2, 3, ... If this is not the
case the message "(N+1)**2 where N is the spherical harmonics order" might be
used to give feedback to the user.


convention.json
---------------

Validation rules in dependency of the convention that a SOFA file is using. The
file contains a list of conventions, with two possible types of entries. First,
a name of a variable or attribute followed by the allowed values, and second,
restrictions of the API (Dimensions of the underlying NetCDF file).

For example, if the convention is "SimpleFreeFieldHRIR", the attribute
"GLOBAL_DataType" must be "FIR" and the dimensions "E" must be 1.


data_type.json
--------------

Validation rule depending on the data type (FIR/FIRe/FIR-E, TF/TFE/TF-E, SOS).
This file contains a list of data types followed by a list of variables and
attributes and their possible values (a value of null denotes that a variable
or attribute must be contained in the SOFA file but that there is no
restriction on the content). Note that only the first letters of the data type
are given, e.g., "FIR" refers to the data types "FIR", "FIR-E", and
"FIRE" (legacy).

For example if the data type is "FIR" (or "FIR-E" or "FIRE") the SOFA file must
contain "Data_IR", "Data_Delay", and "Data_SamplingRate" (with arbitrary
values) and "Data_SamplingRate_Units" with the value "hertz". In this case the
additional entry "hertz" can be used to give feedback to the user.


data.json
---------

Validation rules for single variables and attributes. The file contains a list
of variables and attributes followed by possible values and optionally by
depending variables and their allowed values (a value of null denotes that a
variable or attribute must be contained in the SOFA file but that there is no
restriction on the content).

For example the "ListenerView_Type" must be "cartesian" or "spherical" and if
it is contained in a SOFA file the "ListenerView_Units" must be provided as
well with the values "metre" or "degree, degree, metre"


unit_aliases.json
-----------------
Contains a list of possible variants of unit names. For example the unit
"metre" can also be written "metres", "meter", and "meters".
