import logging
from typing import Union

import pandas as pd

from csv_detective.load_tests import return_all_tests
from .parsing.load import load_file

logging.basicConfig(level=logging.INFO)

tests = {
    t.__name__.split(".")[-1]: t._is
    for t in return_all_tests("ALL", "detect_fields")
}


def validate(
    file_path: str,
    previous_analysis: dict,
    num_rows: int = 500,
    encoding: str = None,
    sep: str = None,
    verbose: bool = False,
    skipna: bool = True,
    sheet_name: Union[str, int] = None,
) -> tuple[bool, pd.DataFrame, dict]:
    """
    Verify is the given file has the same fields and types as in the previous analysis.
    """
    table, analysis = load_file(
        file_path=file_path,
        num_rows=num_rows,
        encoding=encoding,
        sep=sep,
        verbose=verbose,
        sheet_name=sheet_name,
    )
    if verbose:
        logging.info("Comparing table with the previous analysis")
        logging.info("- Checking if all columns match")
    if (
        any(col_name not in list(table.columns) for col_name in previous_analysis["columns"])
        or any(col_name not in list(previous_analysis["columns"].keys()) for col_name in table.columns)
    ):
        logging.warning("> Columns do not match, proceeding with full analysis")
        return False, table, analysis
    for col_name, args in previous_analysis["columns"].items():
        if verbose:
            logging.info(f"- Testing {col_name} for {args['format']}")
        if args["format"] == "string":
            # no test for columns that have not been recognized as a specific format
            continue
        test_func = tests[args["format"]]
        col_data = table[col_name]
        if skipna:
            col_data = col_data.loc[~col_data.isna()]
        if not col_data.apply(test_func).all():
            logging.warning("> Test failed, proceeding with full analysis")
            return False, table, analysis
    if verbose:
        logging.info("> All checks successful")
    return True, table, analysis | {
        k: previous_analysis[k] for k in [
            "categorical",
            "columns",
            "columns_fields",
            "columns_labels",
            "formats",
        ]
    }
