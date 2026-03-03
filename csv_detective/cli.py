"""
Command line client for csv_detective
"""

import argparse
import json

import numpy as np

from csv_detective.explore_csv import routine


class _NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def run():
    explorer = argparse.ArgumentParser(description="Analyse a tabular file")
    explorer.add_argument("file_path", type=str, help="Enter path of tabular file to explore")
    explorer.add_argument(
        "-n",
        "--num_rows",
        dest="num_rows",
        type=int,
        default=500,
        help="Number of rows to use for detection (default 500)",
    )
    explorer.add_argument(
        "-s",
        "--sep",
        dest="sep",
        type=str,
        default=None,
        help="Columns separator (detected if not specified)",
    )
    explorer.add_argument(
        "--save",
        dest="save_results",
        action="store_true",
        default=False,
        help="Save the resulting analysis to json",
    )
    explorer.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        default=False,
        help="Verbose output",
    )

    opts = explorer.parse_args()

    inspection_results = routine(
        file_path=opts.file_path,
        num_rows=opts.num_rows,
        sep=opts.sep,
        save_results=opts.save_results,
        verbose=opts.verbose,
    )

    print(json.dumps(inspection_results, indent=4, ensure_ascii=False, cls=_NumpyEncoder))
