# Changelog

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
