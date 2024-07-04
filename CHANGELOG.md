# Changelog

## Current (in progress)

- Nothing yet

## 0.7.1 (2024-03-27)

- Fixes after production release in hydra

## 0.7.0 (2024-03-21)

- Handle other file formats: xls, xlsx, ods (and more)
- Handle analysis through URLs

## 0.6.8 (2024-01-18)

- prevent exporting NaN values in profile
- raise ValueError if analyzed file has various number of columns across first rows

## 0.6.7 (2024-01-15)

- Add logs for columns that would take too much time within a specific test
- Refactor some tests to improve performances and make detection more accurate
- Try alternative ways to clean text

## 0.6.6 (2023-11-24)

- Change setup.py to better convey dependencies

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
