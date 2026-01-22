import logging
from collections import defaultdict

import pandas as pd

from csv_detective.format import FormatsManager
from csv_detective.parsing.columns import MAX_NUMBER_CATEGORICAL_VALUES, test_col_val

# VALIDATION_CHUNK_SIZE is bigger than (analysis) CHUNK_SIZE because
# it's faster to validate so we can afford to load more rows
VALIDATION_CHUNK_SIZE = int(1e5)
logging.basicConfig(level=logging.INFO)

formats = FormatsManager().formats


def validate(
    file_path: str,
    previous_analysis: dict,
    verbose: bool = False,
    skipna: bool = True,
) -> tuple[bool, dict | None, dict[str, pd.Series] | None]:
    """
    Verify is the given file has the same fields and formats as in the given analysis.

    Args:
        file_path: the path of the file to validate
        previous_analysis: the previous analysis to validate against (expected in the same structure as the output of the routine)
        verbose: whether the code displays the steps it's going through
        skipna: whether to ignore NaN values in the checks
    """
    if verbose:
        logging.info(f"Checking given formats exist")
    for col_name, detected in previous_analysis["columns"].items():
        if detected["format"] == "string":
            continue
        elif detected["format"] not in formats:
            if verbose:
                logging.warning(f"> Unknown format `{detected['format']}` in analysis")
            return False, None, None
    try:
        if previous_analysis.get("separator"):
            # loading the table in chunks
            chunks = pd.read_csv(
                file_path,
                dtype=str,
                sep=previous_analysis["separator"],
                encoding=previous_analysis["encoding"],
                skiprows=previous_analysis["header_row_idx"],
                compression=previous_analysis.get("compression"),
                chunksize=VALIDATION_CHUNK_SIZE,
            )
            analysis = {
                k: v
                for k, v in previous_analysis.items()
                if k
                in ["encoding", "separator", "compression", "heading_columns", "trailing_columns"]
                and v is not None
            }
        else:
            # or chunks-like if not chunkable
            chunks = iter(
                [
                    pd.read_excel(
                        file_path,
                        dtype=str,
                        engine=previous_analysis["engine"],
                        sheet_name=previous_analysis["sheet_name"],
                    )
                ]
            )
            analysis = {k: v for k, v in previous_analysis.items() if k in ["engine", "sheet_name"]}
        analysis.update(
            {k: v for k, v in previous_analysis.items() if k in ["header_row_idx", "header"]}
        )
    except Exception as e:
        if verbose:
            logging.warning(f"> Could not load the file with previous analysis values: {e}")
        return False, None, None
    if verbose:
        logging.info("Comparing table with the previous analysis")
        logging.info(
            f"Testing previously detected formats on chunks of {VALIDATION_CHUNK_SIZE} rows"
        )

    # will contain hashes of each row of the file as index and the number of times
    # each hash was seen as values; used to compute nb_duplicates
    row_hashes_count = pd.Series()
    # will contain the number of times each value of each column is seen in the whole file
    # used for profile to read the file only once
    # naming it "count" to be iso with how col_values are made in detect_formats
    col_values: defaultdict[str, pd.Series] = defaultdict(lambda: pd.Series(name="count"))
    analysis["total_lines"] = 0
    checked_values: dict[str, int] = {col_name: 0 for col_name in previous_analysis["columns"]}
    valid_values: dict[str, int] = {col_name: 0 for col_name in previous_analysis["columns"]}
    for idx, chunk in enumerate(chunks):
        if verbose:
            logging.info(f"- Testing chunk number {idx}")
        if idx == 0:
            if verbose:
                logging.info("Checking if all columns match")
            if len(chunk.columns) != len(previous_analysis["header"]) or any(
                list(chunk.columns)[k] != previous_analysis["header"][k]
                for k in range(len(previous_analysis["header"]))
            ):
                if verbose:
                    logging.warning("> Columns in the file do not match those of the analysis")
                return False, None, None
        analysis["total_lines"] += len(chunk)
        row_hashes_count = row_hashes_count.add(
            pd.util.hash_pandas_object(chunk, index=False).value_counts(),
            fill_value=0,
        )
        for col_name, detected in previous_analysis["columns"].items():
            if verbose:
                logging.info(f"- Testing {col_name} for {detected['format']}")
            if detected["format"] == "string":
                # no test for columns that have not been recognized as a specific format
                continue
            to_check = chunk[col_name].dropna() if skipna else chunk[col_name]
            chunk_valid_values = sum(to_check.apply(formats[detected["format"]].func))
            if formats[detected["format"]].proportion == 1 and chunk_valid_values < len(to_check):
                # we can early stop in this case, not all values are valid while we want 100%
                if verbose:
                    logging.warning(
                        f"> Test failed for column {col_name} with format {detected['format']}"
                    )
                return False, None, None
            checked_values[col_name] += len(to_check)
            valid_values[col_name] += chunk_valid_values
            col_values[col_name] = (
                col_values[col_name]
                .add(
                    chunk[col_name].value_counts(dropna=False),
                    fill_value=0,
                )
                .rename_axis(col_name)
            )  # rename_axis because *sometimes* pandas doesn't pass on the column's name ¯\_(ツ)_/¯
        del chunk
    # finally we loop through the formats that accept less than 100% valid values to check the proportion
    for col_name, detected in previous_analysis["columns"].items():
        if (
            checked_values[col_name] > 0
            and valid_values[col_name] / checked_values[col_name]
            < formats[detected["format"]].proportion
        ):
            if verbose:
                logging.warning(
                    f"> Test failed for column {col_name} with format {detected['format']}"
                )
            return False, None, None
    if verbose:
        logging.info("> All checks successful")
    analysis["nb_duplicates"] = sum(row_hashes_count > 1)
    del row_hashes_count
    analysis["categorical"] = [
        col for col, values in col_values.items() if len(values) <= MAX_NUMBER_CATEGORICAL_VALUES
    ]
    return (
        True,
        analysis
        | {
            k: previous_analysis[k]
            for k in [
                "categorical",
                "columns",
                "columns_fields",
                "columns_labels",
                "formats",
            ]
        },
        col_values,
    )
