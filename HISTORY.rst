History
=======

0.3.1 (2022-03-21)
------------------
* Improvement `sofar.read`: Files with unknown Convention versions can now be read by updating to the latest or a specific version.
* Improvement `sofar.read`: Reporting custom variables when reading SOFA files from disk is now optional and no longer a warning.
* Improvement `Sofa.inspect`: SOFA objects that violate the SOFA convention can now be inspected. In this case, the violations are printed as message instead of raising an Error.
* Improvement `Sofa.verify`: SOFA objects can now be verified without any output in case the output is not desired when calling `Sofa.inspect`.

0.3.0 (2022_03_02)
------------------
* Feature: Add `sofar.inspect` function to get a quicker and better overview of the data inside a SOFA object
* Documentation: Add example of plotting HRIRs/HRTFs on the horizontal plane using pyfar>=0.4.0


0.2.0 (2022_02_14)
------------------
* Feature: Add `Sofa.delete` function to delete optional variables and attributes from SOFA objects
* Bugfix: sofar.read_sofa added data with default values from the SOFA convention even if the data were not contained in the SOFA-files. This is now fixed.
* Bugfix: N:LongName (attribute for SOFA conventions of Type TF, TF-E and TFE) is now optional as defined in AES69-2020.
* Improvement: Do not change time stamp of SOFA files in `sofar.read_sofa`
* Improvement: Multi-unit strings, e.g., 'degree, degree, meter' can now also be separated by spaces or commas only, e.g., 'degree degree,meter' as suggested by AES69-2020 (Issue #21)
* Improvement: Add testing for creating, writing, and reading Sofa files containing only mandatory data.

0.1.4 (2021-12-03)
------------------
* Bugfix: Patch for correctly creating Sofa objects if the path to sofar contains underscores '_'

0.1.3 (2021-11-19)
------------------
* Testing: Add missing dependency to setup.py
* Testing: Only test wheel during CI

0.1.2 (2021-11-18)
------------------
* Bugfix: Patch for correctly loading SOFA files with custom data

0.1.1 (2021-11-12)
------------------
* Documentation: Add examples for using pyfar to work with sofar and SOFA files

0.1.0 (2021-10-29)
------------------
* First release on PyPI