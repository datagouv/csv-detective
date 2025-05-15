import json
import os
from typing import Optional, Union

import pandas as pd

from csv_detective.utils import is_url
from .dataframe import cast_df
from .profile import create_profile
from .schema import generate_table_schema


def generate_output(
    table: pd.DataFrame,
    analysis: dict,
    file_path: str,
    num_rows: int = 500,
    limited_output: bool = True,
    save_results: Union[bool, str] = True,
    output_profile: bool = False,
    output_schema: bool = False,
    output_df: bool = False,
    cast_json: bool = True,
    verbose: bool = False,
    sheet_name: Optional[Union[str, int]] = None,
) -> Union[dict, tuple[dict, pd.DataFrame]]:

    if output_profile:
        analysis["profile"] = create_profile(
            table=table,
            dict_cols_fields=analysis["columns"],
            num_rows=num_rows,
            limited_output=limited_output,
            verbose=verbose,
        )

    if save_results:
        if isinstance(save_results, str):
            output_path = save_results
        else:
            output_path = os.path.splitext(file_path)[0]
            if is_url(output_path):
                output_path = output_path.split('/')[-1]
            if analysis.get("sheet_name"):
                output_path += "_sheet-" + str(sheet_name)
            output_path += ".json"
        with open(output_path, "w", encoding="utf8") as fp:
            json.dump(analysis, fp, indent=4, separators=(",", ": "), ensure_ascii=False)

    if output_schema:
        analysis["schema"] = generate_table_schema(
            analysis,
            save_file=False,
            verbose=verbose
        )

    if output_df:
        return analysis, cast_df(
            df=table,
            columns=analysis["columns"],
            cast_json=cast_json,
            verbose=verbose,
        )
    return analysis
