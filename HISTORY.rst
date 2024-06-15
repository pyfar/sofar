History
=======

1.1.4 (2024-06-15)
------------------
* Update for numpy 2.0 (PR #100)

1.1.3 (2024-3-15)
-----------------
* Update documentation to pydata theme (PR #78)
* Update testing for pytest 8.0 and above (PR #79)

1.1.2 (2024-2-22)
-----------------
* Fix for working with rye package manager (PR #75)
* Add testing for Python 3.12 (PR #76)

1.1.1 (2023-7-7)
----------------
* Fix deploying to PyPi.org

1.1.0 (2023-7-7)
----------------
* Deprecate FreeFieldDirectivityTV 1.0 in favor of FreeFieldDirectivityTV 1.1 (according to sofaconventoins.org and AES69-2022)
* Add `sofar.read_sofa_as_netcdf` for reading SOFA files with erroneous data
* Document SOFA conventions on https://sofar.readthedocs.io/en/stable/resources/conventions.html. `Sofa.info()` will this be deprecated in sofar v1.3.0
* `sofar.read_sofa` and `sofar.write_sofa` now accept filenames and path objects
* Add testing for Python 3.11

1.0.0 (2022-12-16)
------------------
* Use SOFA conventions of version 2.1 from https://github.com/pyfar/sofa_conventions
* Verify SOFA data against all rules defined in the SOFA standard AES69-2022
* Add `Sofa.upgrade_convention` for upgrading outdated conventions. This now uses explicit upgrade rules from https://github.com/pyfar/sofa_conventions
* Remove upgrade functionality from `Sofa.verify`, `sofar.write_sofa`, and `sofar.read_sofa` for a more clear separation of functionality
* Add `Sofa.add_missing` to add missing default data to a SOFA object using the default values specified by the SOFA convention
* Add default parameter value to `Sofa.info`
* Make `sofar.update_conventions` a public function again
* Improve documentation and verbosity of command line output
* Add private function to check congruency of conventions stored as part of SOFAtoolbox and on sofaconventions.org
* Move to Circle CI and improve testing

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