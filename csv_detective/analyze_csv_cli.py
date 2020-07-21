'''Analyzes a folder of csv files with csv_detective. The column type detection is done with
  both the Rule Based (RB) and/or Machine Learning (ML) approaches.
  Saves the results as a JSON file.

Usage:
    analyze_csv_cli.py <i> <j> <k> [options]

Arguments:
    <i>                                An input directory with csvs(if dir it will convert all txt files inside).
    <j>                                An output directory with csvs(if dir it will convert all txt files inside).
    <k>                                Date to process
    --analysis_type ANALYSIS_TYPE          The type of column type analysis: rule, mlearning, both [default: "both":str]
    --num_files NFILES                 Number of files (CSVs) to work with [default: 10:int]
    --num_rows NROWS                   Number of rows per file to use [default: 500:int]
    --num_cores=<n> CORES                  Number of cores to use [default: 1:int]
'''
import datetime
import json

import joblib
from argopt import argopt
from explore_csv import routine
from joblib import Parallel, delayed
from tqdm import tqdm
import os
import logging

from prediction import get_columns_ML_prediction, get_columns_types
from detect_fields_ml.utils_ml.files_io import get_files

ML_MODEL = None
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

TODAY = str(datetime.datetime.today()).split()[0]


def analyze_csv(file_path, analysis_type="both", pipeline=None, num_rows=500, resourceID=None, date_process=TODAY):
    logger.info(" csv_detective on {}".format(file_path))
    final_id = resourceID
    try:
        if analysis_type == "both" or analysis_type == "rule":
            logger.info(f"Starting vanilla CSV Detective on file {file_path}")
            dict_result = routine(file_path, num_rows=num_rows)

            if "columns" in dict_result:
                dict_result["columns"] = {k.strip('"'): v for k, v in dict_result["columns"].items()}
                dict_result["columns_rb"] = dict_result["columns"]
                dict_result.pop("columns")
        else:
            # Get ML tagging
            logger.info(f"Starting ML CSV Detective on file {file_path}")
            dict_result = routine(file_path, num_rows=num_rows, user_input_tests=None)

        if analysis_type != "rule":
            assert pipeline is not None
            y_pred, csv_info = get_columns_ML_prediction(file_path, pipeline,
                                                         dict_result, num_rows=num_rows)
            dict_result["columns_ml"] = get_columns_types(y_pred, csv_info)


    except Exception as e:
        logger.info("Analyzing file {0} failed with {1}".format(file_path, e))
        return final_id, {"error": "{}".format(e)}

    dict_result['analysis_date'] = date_process

    return final_id, dict_result


if __name__ == '__main__':
    parser = argopt(__doc__).parse_args()
    csv_folder_path = parser.i
    dest_folder = parser.j
    date_process = parser.k
    analysis_type = parser.analysis_type
    num_files = parser.num_files
    num_rows = parser.num_rows
    n_jobs = int(parser.num_cores)

    analysis_name = os.path.basename(os.path.dirname(csv_folder_path))
    if analysis_type != "rule":
        logger.info("Loading ML model...")
        ML_MODEL = joblib.load('csv_detective/detect_fields_ml/models/model.joblib')

    if os.path.exists(csv_folder_path):
        if os.path.isfile(csv_folder_path):
            list_files = [csv_folder_path]
        else:
            list_files = get_files(csv_folder_path, sample=None)
    else:
        logger.info("No file/folder found to analyze. Exiting...")
        exit(1)

    if n_jobs and n_jobs > 1:
        csv_info = Parallel(n_jobs=n_jobs)((file_path.split("/")[-1].split(".csv")[0],
                                            delayed(routine)(file_path, analysis_type=analysis_type,
                                                             num_rows=num_rows,
                                                             model_ML=ML_MODEL,
                                                             date_process=date_process))
                                           for file_path in tqdm(list_files))
    else:
        csv_info = [(file_path.split("/")[-1].split(".csv")[0],
                     routine(file_path, analysis_type=analysis_type,
                             num_rows=num_rows,
                             model_ML=ML_MODEL,
                             date_process=date_process))
                    for file_path in tqdm(list_files)]

        # csv_info = [analyze_csv(f, analysis_type=analysis_type, pipeline=ML_PIPELINE, num_rows=num_rows,
        #                          resourceID=f.split("/")[-1].split(".csv")[0], date_process=date_process)
        #             for f in tqdm(list_files)]

    logger.info("Saving info to JSON")

    json.dump(csv_info, open(f"{dest_folder}/{date_process}.json", "w"),
              indent=4)
