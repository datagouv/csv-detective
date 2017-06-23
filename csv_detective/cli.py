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
        user_input_tests='ALL'
    )

    print(json.dumps(inspection_results, indent=4, sort_keys=True, ensure_ascii=False))

    # file_dir = os.path.split(opts.file_path)[0]
    # file_name = os.path.split(opts.file_path)[1]
    #
    #
    # acsz = opts.acsz
    # if acsz:
    #     fields = {'house_num_and_street_name': acsz[0].split(','),
    #                 'city': acsz[1].split(','),
    #                 'state': acsz[2].split(','),
    #                 'zip_code': acsz[3].split(',')
    #                 }
    #     if not (opts.house_num_and_street_name is None \
    #             and opts.city is None \
    #             and opts.state is None \
    #             and opts.zip_code is None):
    #         print('Input Error : you have used --acsz argument. You can therefore not use individual arguments to define columns')
    #         return
    #     if len(acsz) != 4:
    #         print('Input Error: --ascz should take exactly four arguments')
    #         return
    # else:
    # fields = {'house_num_and_street_name': opts.house_num_and_street_name,
    #             'city': opts.city,
    #             'state': opts.state,
    #             'zip_code': opts.zip_code
    #             }
    # if any([column_name is None for column_name in [opts.house_num_and_street_name, opts.city, opts.state, opts.zip_code]]):
    #     print('Input Error : All columns have not been defined')
    #     return
    #
    # run_geocoder(file_dir, file_name, fields, opts.force, opts.delete_cache)
