import logging

import pandas as pd

from csv_detective.format import FormatsManager
from csv_detective.parsing.columns import MAX_NUMBER_CATEGORICAL_VALUES, test_col_val

VALIDATION_CHUNK_SIZE = int(1e5)
logging.basicConfig(level=logging.INFO)

formats = FormatsManager().formats


def validate(
    file_path: str,
    previous_analysis: dict,
    verbose: bool = False,
    skipna: bool = True,
) -> tuple[bool, pd.DataFrame | None, dict | None, dict[str, pd.Series] | None]:
    """
    Verify is the given file has the same fields and types as in the given analysis.

    Args:
        file_path: the path of the file to validate
        previous_analysis: the previous analysis to validate against (expected in the same structure as the output of the routine)
        verbose: whether the code displays the steps it's going through
        skipna: whether to ignore NaN values in the checks
    """
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
        first_chunk = next(chunks)
        analysis.update(
            {k: v for k, v in previous_analysis.items() if k in ["header_row_idx", "header"]}
        )
    except Exception as e:
        if verbose:
            logging.warning(f"> Could not load the file with previous analysis values: {e}")
        return False, None, None, None
    if verbose:
        logging.info("Comparing table with the previous analysis")
        logging.info("- Checking if all columns match")
    if len(first_chunk.columns) != len(previous_analysis["header"]) or any(
        list(first_chunk.columns)[k] != previous_analysis["header"][k]
        for k in range(len(previous_analysis["header"]))
    ):
        if verbose:
            logging.warning("> Columns do not match, proceeding with full analysis")
        return False, None, None, None
    if verbose:
        logging.info(
            f"Testing previously detected formats on chunks of {VALIDATION_CHUNK_SIZE} rows"
        )

    # hashing rows to get nb_duplicates
    row_hashes_count = first_chunk.apply(lambda row: hash(tuple(row)), axis=1).value_counts()
    # getting values for profile to read the file only once
    col_values = {col: first_chunk[col].value_counts(dropna=False) for col in first_chunk.columns}
    analysis["total_lines"] = 0
    for idx, chunk in enumerate([first_chunk, *chunks]):
        if verbose:
            logging.info(f"> Testing chunk number {idx}")
        analysis["total_lines"] += len(chunk)
        row_hashes_count = row_hashes_count.add(
            chunk.apply(lambda row: hash(tuple(row)), axis=1).value_counts(),
            fill_value=0,
        )
        for col in chunk.columns:
            col_values[col] = col_values[col].add(
                chunk[col].value_counts(dropna=False),
                fill_value=0,
            )
        for col_name, args in previous_analysis["columns"].items():
            if verbose:
                logging.info(f"- Testing {col_name} for {args['format']}")
            if args["format"] == "string":
                # no test for columns that have not been recognized as a specific format
                continue
            test_result: float = test_col_val(
                serie=chunk[col_name],
                format=formats[args["format"]],
                skipna=skipna,
            )
            if not bool(test_result):
                if verbose:
                    logging.warning("> Test failed, proceeding with full analysis")
                return False, first_chunk, analysis, None
    if verbose:
        logging.info("> All checks successful")
    analysis["nb_duplicates"] = sum(row_hashes_count > 1)
    analysis["categorical"] = [
        col for col, values in col_values.items() if len(values) <= MAX_NUMBER_CATEGORICAL_VALUES
    ]
    return (
        True,
        first_chunk,
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
