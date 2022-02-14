History
=======

0.1.4 (2022_02_14)
------------------
* Feature: Add `Sofa.delete` function to delete optional variables and attributes from SOFA objects
* Bugfix: sofar.read_sofa added data with default values from the SOFA convention even if the data were not contained in the SOFA-files. This is now fixed.
* Bugfix: N:LongName (attribute for SOFA conventions of Type TF, TF-E and TFE) is now optional as defined in AES69-2020.
* Improvement: Do not change time stamp of SOFA files in `sofar.read_sofa`
* Improvement: Multi-unit strings, e.g., 'degree, degree, meter' can now also be separated by spaces or commas only, e.g., 'degree degree,meter' as suggested by AES69-2020 (Issue #21)
* Improvement: Add testing for creating, writing, and reading Sofa files containing only mandatory data.

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