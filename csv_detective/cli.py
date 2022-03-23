"""
Command line client for csv_detective
"""

import argparse
import json
from .explore_csv import routine


def run():
    explorer = argparse.ArgumentParser(description='Get the arguments we want')
    explorer.add_argument(
        'file_path',
        type=str,
        help='Enter path of csv file to explore'
    )
    explorer.add_argument(
        '-n',
        '--num_rows',
        dest='num_rows',
        type=int,
        nargs='?',
        help='Number of rows to use for detection'
    )
    explorer.add_argument(
        '-t',
        '--select_tests',
        dest='city',
        type=str,
        nargs='*',
        help='List of tests to be performed (use "" if you want to use the dash option to remove tests)'
    )

    opts = explorer.parse_args()

    num_rows = opts.num_rows or 50
    inspection_results = routine(
        opts.file_path,
        num_rows=num_rows,
        user_input_tests='ALL',
        output_mode='ALL'
    )

    print(json.dumps(inspection_results, indent=4, sort_keys=True, ensure_ascii=False))
