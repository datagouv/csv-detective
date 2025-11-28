# CSV Detective

This is a package to **automatically detect column content in tabular files**. The script reads either the whole file or the first few rows and performs various checks (regex, casting, comparison with official lists...) to see for each column if it matches with various content types.

Currently supported file types: csv, xls, xlsx, ods.

You can also directly feed the URL of a remote file (from data.gouv.fr for instance).

## How To?

### Install the package

You need to have Python >= 3.10 installed. We recommend using a virtual environment.

```bash
pip install csv-detective
```

### Detect some columns

Say you have a tabular file located at `file_path`. This is how you could use `csv_detective`:

```python
# Import the csv_detective package
from csv_detective import routine
import os # for this example only

# Replace by your file path
file_path = os.path.join('.', 'tests', 'code_postaux_v201410.csv')

# Open your file and run csv_detective
inspection_results = routine(
  file_path, # or file URL
  num_rows=-1, # Value -1 will analyze all lines of your file, you can change with the number of lines you wish to analyze
  save_results=False, # Default False. If True, it will save result output into the same directory as the analyzed file, using the same name as your file and .json extension
  output_profile=True, # Default False. If True, returned dict will contain a property "profile" indicating profile (min, max, mean, tops...) of every column of your csv
  output_schema=True, # Default False. If True, returned dict will contain a property "schema" containing basic [tableschema](https://specs.frictionlessdata.io/table-schema/) of your file. This can be used to validate structure of other csv which should match same structure. 
)
```

## So What Do You Get ?

### Output

The program creates a `Python` dictionary with the following information :

```
{
    "encoding": "windows-1252", 			        # Encoding detected
    "separator": ";",						# Detected CSV separator
    "header_row_idx": 0					# Index of the header (aka how many lines to skip to get it)
    "headers": ['code commune INSEE', 'nom de la commune', 'code postal', "libellé d'acheminement"], # Header row
    "total_lines": 42,					# Number of rows (excluding header)
    "nb_duplicates": 0,					# Number of exact duplicates in rows
    "heading_columns": 0,					# Number of heading columns
    "trailing_columns": 0,					# Number of trailing columns
    "categorical": ['Code commune']         # Columns that contain less than 25 different values (arbitrary threshold)
    "columns": { # Property that conciliate detection from labels and content of a column
        "Code commune": {
            "python_type": "string",
            "format": "code_commune_insee",
            "score": 1.0
        },
    },
    "columns_labels": { # Property that return detection from header columns
        "Code commune": {
            "python_type": "string",
            "format": "code_commune_insee",
            "score": 0.5
        },
    },
    "columns_fields": { # Property that return detection from content columns
        "Code commune": {
            "python_type": "string",
            "format": "code_commune_insee",
            "score": 1.25
        },
    },
    "profile": {
      "column_name" : {
        "min": 1, # only int and float
        "max": 12, # only int and float
        "mean": 5, # only int and float
        "std": 5, # only int and float
        "tops": [  # 10 most frequent values in the column
          "xxx",
          "yyy",
          "..."
        ],
        "nb_distinct": 67, # number of distinct values
        "nb_missing_values": 102 # number of empty cells in the column
      }
    },
    "schema": { # TableSchema of the file if `output_schema` was set to `True`
      "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
      "name": "",
      "title": "",
      "description": "",
      "countryCode": "FR",
      "homepage": "",
      "path": "https://github.com/datagouv/csv-detective",
      "resources": [],
      "sources": [
        {"title": "Spécification Tableschema", "path": "https://specs.frictionlessdata.io/table-schema"},
        {"title": "schema.data.gouv.fr", "path": "https://schema.data.gouv.fr"}
      ],
      "created": "2023-02-10",
      "lastModified": "2023-02-10",
      "version": "0.0.1",
      "contributors": [
        {"title": "Table schema bot", "email": "schema@data.gouv.fr", "organisation": "data.gouv.fr", "role": "author"}
      ],
      "fields": [
        {
          "name": "Code commune",
          "description": "Le code INSEE de la commune",
          "example": "23150",
          "type": "string",
          "formatFR": "code_commune_insee",
          "constraints": {
            "required": False,
            "pattern": "^([013-9]\\d|2[AB1-9])\\d{3}$",
          }
        }
      ]
    }
}
```

The output slightly differs depending on the file format:
- csv files have `encoding` and `separator` (and `compression` if relevant)
- xls, xlsx, ods files have `engine` and `sheet_name`

You may also set `output_df` to `True`, in which case the output is a tuple of two elements:
- the analysis (as described above)
- an iterator of `pd.DataFrame`s which contain the columns cast with the detected types (which can be used with `pd.concat` or in a loop):
```python
inspection, df_chunks = routine(
    file_path=file_path,
    num_rows=-1,
    output_df=True,
)
cast_df = pd.concat(df_chunks, ignore_index=True)
# if "col1" has been detected as a float, then cast_df["col1"] contains floats
```

### What Formats Can Be Detected

Includes :
- types (float, int, dates, datetimes, JSON) and more specific (latitude, longitude, geoJSON...) 
- Communes, Départements, Régions, Pays
- Codes Communes, Codes Postaux, Codes Departement, ISO Pays
- Codes CSP, Description CSP, SIREN
- E-Mails, URLs, Téléphones FR
- Years, Dates, Jours de la Semaine FR
- UUIDs, Mongo ObjectIds

### Validation
If you have a pre-made analysis of a file, you can check whether another file conforms to the same analysis:
```python
from csv_detective import validate
is_valid, *_ = validate(
  file_path,
  previous_analysis,  # exactly as it came out from the routine function
)
```

### Format detection and scoring
For each column, 3 scores are computed for each format, the higher the score, the more likely the format:
- the field score based on the values contained in the column (0.0 to 1.0).
- the label score based on the header of the column (0.0 to 1.0).
- the overall score, computed as `field_score * (1 + label_score/2)` (0.0 to 1.5).

The overall score computation aims to give more weight to the column contents while
still leveraging the column header.

#### `limited_output` - Select the output mode you want for json report

This option allows you to select the output mode you want to pass. To do so, you have to pass a `limited_output` argument to the `routine` function. This variable has two possible values:

- `limited_output` defaults to `True` which means report will contain only detected column formats based on a pre-selected threshold proportion in data. Report result is the standard output (an example can be found above in 'Output' section).
Only the format with highest score is present in the output.
- `limited_output=False` means report will contain a full list of all column format possibilities for each input data columns with a value associated which match to the proportion of found column type in data. With this report, user can adjust its rules of detection based on a specific threshold and has a better vision of quality detection for each columns. Results could also be easily transformed into a dataframe (columns types in column / column names in rows) for analysis and test.

## Improvement suggestions

- Smarter refactors
- Improve performances
- Test other ways to load and process data (`pandas` alternatives)
- Add more and more detection modules...

Related ideas:

- store column names to make a learning model based on column names for (possible pre-screen)
- entity resolution (good luck...)

## Why Could This Be of Any Use?

Organisations such as [data.gouv.fr](http://data.gouv.fr) aggregate huge amounts of un-normalised data. Performing cross-examination across datasets can be difficult. This tool could help enrich the datasets metadata and facilitate linking them together.

[`udata-hydra`](https://github.com/etalab/udata-hydra) is a crawler that checks, analyzes (using `csv-detective`) and APIfies all tabular files from [data.gouv.fr](http://data.gouv.fr).

An early version of this analysis of all resources on data.gouv.fr can be found [here](https://github.com/Leobouloc/data.gouv-exploration).

## Linting

Remember to format, lint, and sort imports with [Ruff](https://docs.astral.sh/ruff/) before committing (checks will remind you anyway):
```bash
pip install .[dev]
ruff check --fix .
ruff format .
```

### 🏷️ Release

The release process uses the [`tag_version.sh`](tag_version.sh) script to create git tags and update [CHANGELOG.md](CHANGELOG.md) and [pyproject.toml](pyproject.toml) automatically.

**Prerequisites**: [GitHub CLI](https://cli.github.com/) (`gh`) must be installed and authenticated, and you must be on the main branch with a clean working directory.

```bash
# Create a new release
./tag_version.sh <version>

# Example
./tag_version.sh 2.5.0

# Dry run to see what would happen
./tag_version.sh 2.5.0 --dry-run
```

The script automatically:
- Updates the version in `pyproject.toml`
- Extracts commits since the last tag and formats them for `CHANGELOG.md`
- Identifies breaking changes (commits with `!:` in the subject)
- Creates a git tag and pushes it to the remote repository
- Creates a GitHub release with the changelog content
