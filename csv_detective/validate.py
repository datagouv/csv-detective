import logging

import pandas as pd

from csv_detective.load_tests import return_all_tests
from csv_detective.parsing.columns import test_col_val
from csv_detective.parsing.load import load_file

logging.basicConfig(level=logging.INFO)

tests = {
    t.__name__.split(".")[-1]: {
        "func": t._is,
        "prop": t.PROPORTION,
    }
    for t in return_all_tests("ALL", "detect_fields")
}


def validate(
    file_path: str,
    previous_analysis: dict,
    num_rows: int = 500,
    encoding: str | None = None,
    sep: str | None = None,
    verbose: bool = False,
    skipna: bool = True,
    sheet_name: str | int | None = None,
) -> tuple[bool, pd.DataFrame | None, dict | None]:
    """
    Verify is the given file has the same fields and types as in the previous analysis.
    """
    try:
        table, analysis = load_file(
            file_path=file_path,
            num_rows=num_rows,
            encoding=encoding,
            sep=sep,
            verbose=verbose,
            sheet_name=sheet_name,
        )
    except Exception as e:
        if verbose:
            logging.warning(f"> Could not load the file with previous analysis values: {e}")
        return False, None, None
    if verbose:
        logging.info("Comparing table with the previous analysis")
        logging.info("- Checking if all columns match")
    if any(col_name not in analysis["header"] for col_name in previous_analysis["header"]) or any(
        col_name not in previous_analysis["header"] for col_name in analysis["header"]
    ):
        if verbose:
            logging.warning("> Columns do not match, proceeding with full analysis")
        return False, None, None
    for col_name, args in previous_analysis["columns"].items():
        if verbose:
            logging.info(f"- Testing {col_name} for {args['format']}")
        if args["format"] == "string":
            # no test for columns that have not been recognized as a specific format
            continue
        test_result: float = test_col_val(
            serie=table[col_name],
            test_func=tests[args["format"]]["func"],
            proportion=tests[args["format"]]["prop"],
            skipna=skipna,
        )
        if not bool(test_result):
            if verbose:
                logging.warning("> Test failed, proceeding with full analysis")
            return False, table, analysis
    if verbose:
        logging.info("> All checks successful")
    return (
        True,
        table,
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
    )
