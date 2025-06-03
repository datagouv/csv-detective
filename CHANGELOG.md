# Changelog

## Current (in progress)

- Refactor label testing [#119](https://github.com/datagouv/csv-detective/pull/119)
- Better URL detection [#120](https://github.com/datagouv/csv-detective/pull/120)

## 0.8.0 (2025-05-20)

- New function that creates a csv from a list of fields and constraints, or from a TableSchema [#101](https://github.com/datagouv/csv-detective/pull/101)
- Enable outputing loaded dataframe [#102](https://github.com/datagouv/csv-detective/pull/102)
- Better naming, hint types and minor refactors [#103](https://github.com/datagouv/csv-detective/pull/103)
- The returned dataframe has its columns properly cast to the detected types [#104](https://github.com/datagouv/csv-detective/pull/104)
- Raise an error if the encoding could not be guessed [#106](https://github.com/datagouv/csv-detective/pull/106)
- Fix CLI and minio routine [#107](https://github.com/datagouv/csv-detective/pull/107)
- Allow to only specify tests to skip ("all but...") [#108](https://github.com/datagouv/csv-detective/pull/108)
- Fix bool casting [#109](https://github.com/datagouv/csv-detective/pull/109)
- Handle csv.gz files [#110](https://github.com/datagouv/csv-detective/pull/110)
- Refactor file tests [#110](https://github.com/datagouv/csv-detective/pull/110)
- Restructure repo (breaking changes) [#111](https://github.com/datagouv/csv-detective/pull/111)
- Add validation function and associated flow [#112](https://github.com/datagouv/csv-detective/pull/112)
- Better float detection [#113](https://github.com/datagouv/csv-detective/pull/113)
- Refactor fields tests [#114](https://github.com/datagouv/csv-detective/pull/114)
- Better code waldec and add code import [#116](https://github.com/datagouv/csv-detective/pull/116)
- Better validation and refactors [#117](https://github.com/datagouv/csv-detective/pull/117)
- Fix validation [#118](https://github.com/datagouv/csv-detective/pull/118)

## 0.7.4 (2024-11-15)

- Enable calling main functions from base [#97](https://github.com/datagouv/csv-detective/pull/97)
- Better detection of ints and floats [#94](https://github.com/datagouv/csv-detective/pull/94)
- Better handle NaN values [#96](https://github.com/datagouv/csv-detective/pull/96)
- Reshape exemple.py, clean up code and improve changelog [#98](https://github.com/datagouv/csv-detective/pull/98)

## 0.7.3 (2024-10-07)

- Refactor tests import, now using folder arborescence instead of pre-made file [#93](https://github.com/datagouv/csv-detective/pull/93)
- Fix inversion (count<=>value) in profile [#95](https://github.com/datagouv/csv-detective/pull/95)

## 0.7.2 (2024-08-27)

- Outsource many formats to fr-format library [#87](https://github.com/datagouv/csv-detective/pull/87)
- Better date detection [#89](https://github.com/datagouv/csv-detective/pull/89)
- Update dependencies to make tests pass [#81](https://github.com/datagouv/csv-detective/pull/81)
- Update readme [#81](https://github.com/datagouv/csv-detective/pull/81)
- Hint type [#81](https://github.com/datagouv/csv-detective/pull/81)
- Minor refactors [#81](https://github.com/datagouv/csv-detective/pull/81)

## 0.7.1 (2024-03-27)

- Fixes after production release in hydra [#80](https://github.com/datagouv/csv-detective/pull/80)

## 0.7.0 (2024-03-21)

- Handle other file formats: xls, xlsx, ods (and more) and analysis through URLs [#73](https://github.com/datagouv/csv-detective/pull/73)
- Handle files with no extension (cc hydra) [#79](https://github.com/datagouv/csv-detective/pull/79)

## 0.6.8 (2024-01-18)

- prevent exporting NaN values in profile [#72](https://github.com/datagouv/csv-detective/pull/72)
- raise ValueError if analyzed file has various number of columns across first rows [#72](https://github.com/datagouv/csv-detective/pull/72)

## 0.6.7 (2024-01-15)

- Add logs for columns that would take too much time within a specific test [#70](https://github.com/datagouv/csv-detective/pull/70)
- Refactor some tests to improve performances and make detection more accurate [#69](https://github.com/datagouv/csv-detective/pull/69)
- Try alternative ways to clean text [#71](https://github.com/datagouv/csv-detective/pull/71)

## 0.6.6 (2023-11-24)

- Change setup.py to better convey dependencies [#67](https://github.com/datagouv/csv-detective/pull/67)

## 0.6.5 (2023-11-17)

- Change encoding detection for faust-cchardet (forked from cchardet) [#66](https://github.com/etalab/csv-detective/pull/66)

## 0.6.4 (2023-10-18)

- Better handling of ints and floats (now not accepting blanks and "+" in string) [#62](https://github.com/etalab/csv-detective/pull/62)

## 0.6.3 (2023-03-23)

- Faster routine [#59](https://github.com/etalab/csv-detective/pull/59)

## 0.6.2 (2023-02-10)

- Catch OverflowError for latitude and longitude checks [#58](https://github.com/etalab/csv-detective/pull/58)

## 0.6.0 (2023-02-10)

- Add CI and upgrade dependencies [#49](https://github.com/etalab/csv-detective/pull/49)
- Shuffle data before analysis [#56](https://github.com/etalab/csv-detective/pull/56)
- Better discrimination between `code_departement` and `code_region` [#56](https://github.com/etalab/csv-detective/pull/56)
- Add schema in output analysis [#57](https://github.com/etalab/csv-detective/pull/57)

## 0.4.7 [#51](https://github.com/etalab/csv-detective/pull/51)

- Allow possibility to analyze entire file instead of a limited number of rows [#48](https://github.com/etalab/csv-detective/pull/48)
- Better boolean detection [#42](https://github.com/etalab/csv-detective/issues/42)
- Differentiate python types and format for `date` and `datetime` [#43](https://github.com/etalab/csv-detective/issues/43)
- Better `code_departement` and `code_commune_insee` detection [#44](https://github.com/etalab/csv-detective/issues/44)
- Fix header line (`header_row_idx`) detection [#44](https://github.com/etalab/csv-detective/issues/44)
- Allow possibility to get profile of csv [#46](https://github.com/etalab/csv-detective/issues/46)

## 0.4.6 [#39](https://github.com/etalab/csv-detective/pull/39)

- Fix tests
- Prioritise lat / lon FR detection over more generic lat / lon.
- To reduce false positives, prevent detection of the following if label detection is missing: `['code_departement', 'code_commune_insee', 'code_postal', 'latitude_wgs', 'longitude_wgs', 'latitude_wgs_fr_metropole', 'longitude_wgs_fr_metropole', 'latitude_l93', 'longitude_l93']`
- Lower threshold of label detection so that if one relevant is detected in the label, it boosts the detection score.
- Add ISO country alpha-3 and numeric detection
- include camel case parsing in _process_text function
- Support optional brackets in latlon format

## 0.4.5 [#29](https://github.com/etalab/csv-detective/pull/29)

- Use `netloc` instead of `url` in location dict

## 0.4.4 [#24] (https://github.com/etalab/csv-detective/pull/28)

- Prevent crash on empty CSVs
- Add optional arguments encoding and sep to routine and routine_minio functions
- Field detection improvements (code_csp_insee and datetime RFC 822)
- Schema generation improvements with examples


## 0.4.3 [#24] (https://github.com/etalab/csv-detective/pull/24)

- Add uuid and MongoID detection
- Add new function dedicated to interaction with minio data
- Add table schema automatic generation (only on minio data)
- Modification of calculated score (consider label detection as a boost for score)

## 0.4.2 [#22] (https://github.com/etalab/csv-detective/pull/22)

Add type detection by header name

## 0.4.1 [#19] (https://github.com/etalab/csv-detective/pull/19)

Fix bug
 * num_rows was causing problem when it was fix to other value than default - Fixed

## 0.4.0 [#18] (https://github.com/etalab/csv_detective/pull/18)

Add detailed output possibility

Details :
 * two modes now for output report : "LIMITED" and "ALL"
 * "ALL" option give user information on found proportion for each column types and each columns

## 0.3.0 [#15] (https://github.com/etalab/csv_detective/pull/15)

Fix bugs

Details :
 * Facilitate ML Integration
 * Add column types detection
 * Fix documentation

## 0.2.1 - [#2](https://github.com/etalab/csv_detective/pull/2)

Add continuous integration

Details :
 * Add configuration for CircleCI
 * Add `CONTRIBUTING.md`
 * Push automatically new versions to PyPI
 * Use semantic versioning

## 0.2 - [#1](https://github.com/etalab/csv_detective/pull/1)

Port from python2 to python3

Details :
 * Add license AGPLv3
 * Update requirements

## 0.1
