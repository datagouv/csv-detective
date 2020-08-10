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

import joblib
from joblib import Parallel, delayed
from argopt import argopt
from tqdm import tqdm

from csv_detective.explore_csv import routine

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

TODAY = str(datetime.datetime.today()).split()[0]


def analyze_csv(file_path, num_rows=500, date_process=TODAY,
                return_probabilities=True, output_mode="ALL"):
    logger.info(" csv_detective on {}".format(file_path))
    try:
        dict_result = routine(file_path, num_rows=num_rows, user_input_tests='ALL', output_mode=output_mode)

    except Exception as e:
        logger.info("Analyzing file {0} failed with {1}".format(file_path, e))
        return {"error": "{}".format(e)}

    dict_result['analysis_date'] = date_process

    return dict_result


if __name__ == '__main__':
    parser = argopt(__doc__).parse_args()
    csv_folder_path = parser.i
    dest_folder = parser.j
    date_process = parser.k
    rb_ml_analysis = parser.rb_ml_analysis
    num_files = parser.num_files
    num_rows = parser.num_rows
    n_jobs = int(parser.num_cores)

    analysis_name = os.path.basename(os.path.dirname(csv_folder_path))
    list_files = []
    if os.path.exists(csv_folder_path):
        if os.path.isfile(csv_folder_path):
            list_files = [csv_folder_path]
        else:
            list_files = get_files(csv_folder_path, sample=None)
    else:
        logger.info("No file/folder found to analyze. Exiting...")
        exit(1)

    if not list_files:
        logger.info("No file/folder found to analyze. Exiting...")
        exit(1)

    if n_jobs and n_jobs > 1:
        csv_info = Parallel(n_jobs=n_jobs)((file_path.split("/")[-1].split(".csv")[0],
                                            delayed(analyze_csv)(file_path,
                                                                 num_rows=num_rows,
                                                                 date_process=date_process))
                                           for file_path in tqdm(list_files))
    else:
        csv_info = []
        for file_path in tqdm(list_files):
            dataset_id = file_path.split("/")[-1].split(".csv")[0]
            analysis_output = analyze_csv(file_path,
                                          num_rows=num_rows,
                                          date_process=date_process,)
            csv_info.append((dataset_id, analysis_output))

    logger.info("Saving info to JSON")
    # check that we have a good result
    #_check_full_report(analysis_output, logger)
    json.dump(csv_info, open(f"{dest_folder}/{date_process}.json", "w"),
              indent=4, ensure_ascii=False)