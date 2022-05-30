# CSV Detective

This is a package to **automatically detect column content in CSV files**. As of now, the script reads the first few rows of the CSV and performs various checks to see for each column if it matches with various content types. This is currently done through regex and string comparison.

Work is still in progress, and you will surely encounter errors when using csv_detective; you might not even be able to get it run once! When this will happen, please feel free to open an issue or make a pull request with a fix.

## How To ?

### Install the package

You need to have python >= 3.4 installed. We recommend using a virtual environement (`pew` or `virtualenvwrapper` for example).

```
pip install csv-detective
```

### Detect some columns

Say you have a CSV file located in `file_path`. This is how you could use `csv_detective`:

```
# Import the csv_detective package
from csv_detective.explore_csv import routine
import os # for this example only
import json # for json dump only

# Replace by your file path
file_path = os.path.join('.', 'tests', 'code_postaux_v201410.csv')

# Open your file and run csv_detective
inspection_results = routine(file_path)

# Write your file as json
with open(file_path.replace('.csv', '.json'), 'w', encoding='utf8') as fp:
    json.dump(inspection_results, fp, indent=4, separators=(',', ': '))

```

## So What Do You Get ?

### Output

The program creates a `Python` dictionnary with the following information : 

```
{
    "heading_columns": 0, 					# Number of heading columns
    "encoding": "windows-1252", 			        # Encoding detected
    "ints_as_floats": [],					# Columns where integers may be represented as floats
    "trailing_columns": 0,					# Number of trailing columns
    "headers": ['code commune INSEE', 'nom de la commune', 'code postal', "libell\\u00e9 d'acheminement\n"], # Header row
    "separator": ";",						# Detected CSV separator
    "headers_row": 0,						# Number of heading rows
    "columns_fields": {
        "nom de la commune": {
            "python_type": "string",
            "format": "commune",
            "score": 1.0
        },
    },
    "columns_labels": {
        "nom de la commune": {
            "python_type": "string",
            "format": "commune",
            "score": 0.5
        },
    },
    "columns_fields": {
        "nom de la commune": {
            "python_type": "string",
            "format": "commune",
            "score": 1.25
        },
    }
}
```

### What Formats Can Be Detected

Includes : 

- Communes, Départements, Régions, Pays
- Codes Communes, Codes Postaux, Codes Departement, ISO Pays
- Codes CSP, Description CSP, SIREN 
- E-Mails, URLs, Téléphones FR
- Years, Dates, Jours de la Semaine FR
- UUIDs, Mongo ObjectIds

### Format detection and scoring
For each column, 3 scores are computed for each format, the higher the score, the more likely the format:
- the field score based on the values contained in the column (0.0 to 1.0).
- the label score based on the header of the column (0.0 to 1.0).
- the overall score, computed as `field_score * (1 + label_score/2)` (0.0 to 1.5).

The overall score computation aims to give more weight to the column contents while
still leveraging the column header.

### Additional options
#### `user_input_tests` - Select the tests you want to pass
This library allows you to select the tests you want to pass. To do so, you have to pass a `user_input_tests` argument to the `routine` function. This variable can be a string or a list of strings and indicates what tests to import. The following rules apply:

- `user_input_tests` defaults to `'ALL'` which means all tests will be passed
- The tests are referenced by their path, with directories seperated by dots. For example we could have `user_input_tests = 'FR.geo'` which means all tests located in the folder `detect_fields\\FR\\geo` will be run.
- Input can also be a list of strings : `['FR.geo', 'temp']` will load all tests in `detect_fields\\FR\\geo` and `detect_fields\\temp`
- When using a list of strings as input, you can also choose to exclude certain test branches by adding a dash before their path : `['ALL', '-FR.geo.code_departement']` will load all tests with the exception of the `code_departement` test.

**Partial code** :
```
tests = ['FR.geo', 'other.email', '-FR.geo.code_departement']

# Open your file and run csv_detective
with open(file_path, 'r') as file:
	inspection_results = routine(file, user_input_tests = tests)
```

#### `output_mode` - Select the output mode you want for json report

This option allows you to select the output mode you want to pass. To do so, you have to pass a `output_mode` argument to the `routine` function. This variable has two possible values:

- `output_mode` defaults to `'LIMITED'` which means report will contain only detected column formats based on a pre-selected threshold proportion in data. Report result is the standard output (an example can be found above in 'Output' section).
Only the format with highest score is present in the output.
- `output_mode='ALL'` which means report will contain a full list of all column format possibilities for each input data columns with a value associated which match to the proportion of found column type in data. With this report, user can adjust its rules of detection based on a specific threshold and has a better vision of quality detection for each columns. Results could also be easily transformed into dataframe (columns types in column / column names in rows) for analysis and test.


**Partial code** :
```
# Open your file and run csv_detective
with open(file_path, 'r') as file:
	inspection_results = routine(file, output_mode='ALL')
```
**Output for output_mode='ALL'**

```
{
  "categorical": [
    "dispositif",
    "volet"
  ],
  "columns": {
    "code_departement": [
      {
        "colonne": "dep",
        "score": 0.8
      },
      {
        "colonne": "reg",
        "score": 0.4
      },
      {
        "colonne": "assoc",
        "score": 0
      }
    ],
    "code_region": [
      {
        "colonne": "dep",
        "score": 0.6
      },
      {
        "colonne": "reg",
        "score": 0.8
      },
      {
        "colonne": "assoc",
        "score": 0
      }
    ],
    "code_rna": [
      {
        "colonne": "dep",
        "score": 0
      },
      {
        "colonne": "reg",
        "score": 0
      },
      {
        "colonne": "assoc",
        "score": 0.9
      }
    ],
    #[... same output format for each column types]
    "header_row_idx": 0,
    "heading_columns": 0,
    "ints_as_floats": [
      "montant_total"
    ],
    "separator": ",",
    "total_lines": 321,
    "trailing_columns": 0
  }
}
```


## TODO (this list is too long)

- Clean up
- Make more robust
- Batch analyse
- Command line interface
- Improve output format
- Improve testing structure to make modular searches (search only for cities for example)
- Get rid of `pandas` dependency
- Improve pre-processing and pre-processing tracing (removing heading rows for example)
- Make differentiated pre-processing (no lower case for country codes for example)
- Give a sense of probability in the prediction
- Add more and more detection modules...

Related ideas:

- store column names to make a learning model based on column names for (possible pre-screen)
- normalising data based on column prediction
- entity resolution (good luck...)

## Why Could This Be of Any Use ?

Organisations such as [data.gouv](http://data.gouv.fr) aggregate huge amounts of un-normalised data. Performing cross-examination across datasets can be difficult. This tool could help enrich the datasets metadata and facilitate linking them together.

[Here](https://github.com/Leobouloc/data.gouv-exploration) is project (just started) that has code to download all csv files from the data.gouv website and analyse them using csv_detective.





