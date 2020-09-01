'''Analyzes a folder of csv files with csv_detective. The column type detection is done with
  both the Rule Based (RB) and/or Machine Learning (ML) approaches.
  Saves the results as a JSON file.
Usage:
    analyze_csv_cli.py <i> <j> <k> [options]
Arguments:
    <i>                                An input directory with csvs(if dir it will convert all txt files inside).
    <j>                                An output directory with csvs(if dir it will convert all txt files inside).
    <k>                                Date to process
    --rb_ml_analysis METHOD            If set, compute both rule-based and machine earning column type detection analysis on the csv
    --num_files NFILES                 Number of files (CSVs) to work with [default: 10:int]
    --num_rows NROWS                   Number of rows per file to use [default: 500:int]
    --num_cores=<n> CORES                  Number of cores to use [default: 1:int]
'''

import datetime
import json
import os
import logging
from pathlib import Path
import argparse
from random import sample

import joblib
from joblib import Parallel, delayed
from tqdm import tqdm

from csv_detective.explore_csv import routine

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

TODAY = str(datetime.datetime.today()).split('.')[0].replace(' ','_').replace(':','-')


def get_files(input_folder, ext=".csv", n_sample=0):
    list_files = []
    for folder in os.listdir(input_folder):
        for file in os.listdir(input_folder / folder):
            # Open your file and run csv_detective
            file_path = input_folder / folder / file

            if file_path.suffix == ext:
                list_files.append(file_path)
    if n_sample > 0:
        list_files = sample(list_files, n_sample)
    return list_files


def analyze_csv(file_path, num_rows=500, date_process=TODAY, output_mode="LIMITED"):
    logger.info(" csv_detective on {}".format(file_path))
    try:
        dict_result = routine(file_path, num_rows=num_rows, user_input_tests='ALL', output_mode=output_mode)

    except Exception as e:
        logger.info("Analyzing file {0} failed with {1}".format(file_path, e))
        return {"error": "{}".format(e)}

    dict_result['analysis_date'] = date_process

    return dict_result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_folder',
                        help='The folder where the csv can be found',
                        required=True)
    parser.add_argument('--output_folder',
                        help='The folder where the output will be made',
                        required=True)
    parser.add_argument('--date_process',
                        default=TODAY)
    parser.add_argument('--num_files',
                        default='10')
    parser.add_argument('--num_rows',
                        default='500')
    parser.add_argument('--num_cores',
                        default='1')
    parser.add_argument('--num_samples',
                        default='0')
    parser.add_argument('--output_mode',
                        default='LIMITED')

    args = parser.parse_args()

    num_files = int(args.num_files)
    num_rows = int(args.num_rows)
    num_cores = int(args.num_cores)

    input_folder = Path(args.input_folder)
    output_folder = Path(args.output_folder)

    analysis_name = os.path.basename(os.path.dirname(args.input_folder))
    list_files = []
    if input_folder.exists():
        list_files = get_files(input_folder, n_sample=int(args.num_samples))
    else:
        logger.info("No file/folder found to analyze. Exiting...")
        exit(1)

    if not list_files:
        logger.info("No file/folder found to analyze. Exiting...")
        exit(1)

    if num_cores > 1:
        csv_info_raw = Parallel(n_jobs=num_cores)(delayed(analyze_csv)(file_path,
                                                                    num_rows=num_rows,
                                                                    date_process=args.date_process,
                                                                       output_mode=args.output_mode)
                                              for file_path in tqdm(list_files))
        csv_info = {file_path.stem: info for (file_path,info) in zip(list_files, csv_info_raw)}

    else:
        csv_info = {}
        for file_path in tqdm(list_files):
            dataset_id = file_path.stems
            analysis_output = analyze_csv(file_path,
                                          num_rows=num_rows,
                                          date_process=args.date_process)
            csv_info[dataset_id] = analysis_output

    logger.info("Saving info to JSON")
    # check that we have a good result
    # _check_full_report(analysis_output, logger)

    # Write your file as json
    output_folder = Path(args.output_folder)
    if not output_folder.exists():
        os.makedirs(output_folder)

    output_file = output_folder / f"{args.date_process}.json"
    with open(output_file, 'w') as fp:
        json.dump(csv_info, fp, indent=4, ensure_ascii=False)
