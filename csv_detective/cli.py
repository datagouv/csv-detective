"""
Command line client for csv_detective
"""

import argparse
import json
from .explore_csv import routine


def run():
    explorer = argparse.ArgumentParser(description="Analyse a tabular file")
    explorer.add_argument(
        "file_path",
        type=str,
        help="Enter path of tabular file to explore"
    )
    explorer.add_argument(
        "-n",
        "--num_rows",
        dest="num_rows",
        type=int,
        nargs="?",
        help="Number of rows to use for detection (default 500)"
    )
    explorer.add_argument(
        "-s",
        "--sep",
        dest="sep",
        type=str,
        nargs="?",
        help="Columns separator (detected if not specified)"
    )
    explorer.add_argument(
        "--save",
        dest="save_results",
        type=int,
        nargs="?",
        help="Whether to save the resulting analysis to json (1 = save, 0 = don't)"
    )
    explorer.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        type=int,
        nargs="?",
        help="Verbose (0 = quiet, 1 = details)"
    )

    opts = explorer.parse_args()

    inspection_results = routine(
        csv_file_path=opts.file_path,
        num_rows=opts.num_rows,
        sep=opts.sep,
        save_results=bool(opts.save_results),
        verbose=bool(opts.verbose),
    )

    print(json.dumps(inspection_results, indent=4, ensure_ascii=False))
