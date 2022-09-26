"""
Ce script analyse les premières lignes d'un CSV pour essayer de déterminer le
contenu possible des champs
"""

from typing import Dict, List, Literal, Optional, Union
import json
from multiprocessing.sharedctypes import Value
import numpy as np
import os
import tempfile
from pkg_resources import resource_string

from csv_detective import detect_fields
from csv_detective import detect_labels
from csv_detective.s3_utils import download_from_minio, upload_to_minio
from csv_detective.schema_generation import generate_table_schema
from csv_detective.utils import test_col, test_label, prepare_output_dict
from .detection import (
    detect_separator,
    detect_encoding,
    detect_headers,
    detect_heading_columns,
    detect_trailing_columns,
    parse_table,
    detetect_categorical_variable, detect_continuous_variable)


#############################################################################
############### ROUTINE DE TEST CI DESSOUS ##################################


def return_all_tests(user_input_tests, detect_type='detect_fields'):
    """
    returns all tests that have a method _is and are listed in the user_input_tests
    the function can select a sub_package from csv_detective
    """
    all_packages = resource_string(__name__, 'all_packages.txt')
    all_packages = all_packages.decode().split('\n')
    all_packages.remove('')
    all_packages.remove('csv_detective')
    all_packages = [x.replace('csv_detective.', '') for x in all_packages]

    if user_input_tests is None:
        return []

    if isinstance(user_input_tests, str):
        assert user_input_tests[0] != '-'
        if user_input_tests == 'ALL':
            tests_to_do = [detect_type]
        else:
            tests_to_do = [detect_type + '.' + user_input_tests]
        tests_to_not_do = []
    elif isinstance(user_input_tests, list):
        if 'ALL' in user_input_tests:
            tests_to_do = [detect_type]
        else:
            tests_to_do = [detect_type + '.' + x for x in user_input_tests if x[0] != '-']
        tests_to_not_do = [detect_type + '.' + x[1:] for x in user_input_tests if x[0] == '-']

    all_fields = [x for x in all_packages if any([y == x[:len(y)] for y in tests_to_do]) and all([y != x[:len(y)] for y in tests_to_not_do])]
    all_tests = [eval(field) for field in all_fields]
    all_tests = [test for test in all_tests if '_is' in dir(test)] # TODO : Fix this shit
    return all_tests


def routine(
    csv_file_path: str,
    num_rows: int=50,
    user_input_tests: Union[str, List[str]]='ALL',
    output_mode: Literal['ALL', 'LIMITED']='LIMITED',
    save_results: bool=True,
    encoding: str=None,
    sep: str=None):
    '''Returns a dict with information about the csv table and possible
    column contents.

    Args:
        csv_file_path: local path to CSV file if not using Minio
        num_rows: number of rows to sample from the file for analysis
        user_input_tests: tests to run on the file
        output_mode: LIMITED or ALL, whether or not to return all possible types or only the most likely one for each column
        save_results: whether or not to save the results in a json file

    Returns:
        dict: a dict with information about the csv and possible types for each column
    '''
    if csv_file_path is None:
        raise ValueError('csv_file_path is required.')

    if encoding is None:
        binary_file = open(csv_file_path, mode='rb')
        encoding = detect_encoding(binary_file)['encoding']

    with open(csv_file_path, 'r', encoding=encoding) as str_file:
        if sep is None:
            sep = detect_separator(str_file)
        header_row_idx, header = detect_headers(str_file, sep)
        if header is None:
            return_dict = {'error': True}
            return return_dict
        elif isinstance(header, list):
            if any([x is None for x in header]):
                return_dict = {'error': True}
                return return_dict
        heading_columns = detect_heading_columns(str_file, sep)
        trailing_columns = detect_trailing_columns(str_file, sep, heading_columns)
        table, total_lines = parse_table(str_file, encoding, sep, num_rows)

    if table.empty:
        res_categorical = []
        res_continuous = []
    else:
        # Detects columns that are categorical
        res_categorical, categorical_mask = detetect_categorical_variable(table)
        res_categorical = list(res_categorical)
        # Detect columns that are continuous (we already know the categorical)
        res_continuous = list(detect_continuous_variable(table.iloc[:, ~categorical_mask.values]))

    # Creating return dictionary
    return_dict = dict()
    return_dict['encoding'] = encoding
    return_dict['separator'] = sep
    return_dict['header_row_idx'] = header_row_idx
    return_dict['header'] = header
    return_dict['total_lines'] = total_lines

    return_dict['heading_columns'] = heading_columns
    return_dict['trailing_columns'] = trailing_columns

    return_dict['continuous'] = res_continuous
    return_dict['categorical'] = res_categorical

    # list testing to be performed
    all_tests_fields = return_all_tests(user_input_tests, detect_type='detect_fields')  #list all tests for the fields
    all_tests_labels = return_all_tests(user_input_tests, detect_type='detect_labels')  # list all tests for the labels

    # if no testing then return
    if not all_tests_fields and not all_tests_labels:
        return return_dict

    # Perform testing on fields
    return_table_fields = test_col(table, all_tests_fields, num_rows, output_mode)
    return_dict_cols_fields = prepare_output_dict(return_table_fields, output_mode)
    return_dict['columns_fields'] = return_dict_cols_fields

    # Perform testing on labels
    return_table_labels = test_label(table, all_tests_labels, output_mode)
    return_dict_cols_labels = prepare_output_dict(return_table_labels, output_mode)
    return_dict['columns_labels'] = return_dict_cols_labels

    # Multiply the results of the fields by 1 + 0.5 * the results of the labels.
    # This is because the fields are more important than the labels and yields a max of 1.5 for the final score.
    return_table = return_table_fields * (1 + return_table_labels.reindex(index=return_table_fields.index, fill_value=0).values / 2)

    # To reduce false positives: ensure these formats are detected only if the label yields a detection.
    formats_with_mandatory_label = ['code_departement', 'code_commune_insee', 'code_postal', 'latitude_wgs', 'longitude_wgs',
        'latitude_wgs_fr_metropole', 'longitude_wgs_fr_metropole', 'latitude_l93', 'longitude_l93']
    return_table.loc[formats_with_mandatory_label, :] = np.where(
                                                            return_table_labels.loc[formats_with_mandatory_label, :],
                                                            return_table.loc[formats_with_mandatory_label, :],
                                                            0)

    return_dict_cols = prepare_output_dict(return_table, output_mode)
    return_dict['columns'] = return_dict_cols

    metier_to_python_type = {
        'booleen': 'bool',
        'int': 'int',
        'float': 'float',
        'string': 'string',
        'latitude': 'float',
        'latitude_l93': 'float',
        'latitude_wgs': 'float',
        'latitude_wgs_fr_metropole': 'float',
        'longitude': 'float',
        'longitude_l93': 'float',
        'longitude_wgs': 'float',
        'longitude_wgs_fr_metropole': 'float',
    }

    if output_mode == 'ALL':
        for detection_method in ['columns_fields', 'columns_labels', 'columns']:
            return_dict[detection_method] = {col_name: [{'python_type': metier_to_python_type.get(detection['format'], 'string'), **detection} for detection in detections] for col_name, detections in return_dict[detection_method].items()}
    if output_mode == 'LIMITED':
        for detection_method in ['columns_fields', 'columns_labels', 'columns']:
            return_dict[detection_method] = {col_name: {'python_type': metier_to_python_type.get(detection['format'], 'string'), **detection} for col_name, detection in return_dict[detection_method].items()}

        # Add detection with formats as keys
        return_dict['formats'] = { column_metadata['format']: [] for column_metadata in return_dict['columns'].values() }
        for header, col_metadata in return_dict['columns'].items():
            return_dict['formats'][col_metadata['format']].append(header)

    if save_results:
        # Write your file as json
        output_path_to_store_minio_file = os.path.splitext(csv_file_path)[0] + '.json'
        with open(output_path_to_store_minio_file, 'w', encoding='utf8') as fp:
            json.dump(return_dict, fp, indent=4, separators=(',', ': '))

    return return_dict


def routine_minio(
    csv_minio_location: Dict[str, str],
    output_minio_location: Dict[str, str],
    tableschema_minio_location: Dict[str, str],
    minio_user: str,
    minio_pwd: str,
    num_rows: int=50,
    user_input_tests: Union[str, List[str]]='ALL',
    encoding: str=None,
    sep: str=None):
    '''Returns a dict with information about the csv table and possible
    column contents.

    Args:
        csv_minio_location: dict with Minio URL, bucket and key of the CSV file
        output_minio_location: Minio URL, bucket and key to store output file. None if not uploading to Minio.
        tableschema_minio_location: Minio URL, bucket and key to store tableschema file. None if not uploading the tableschema to Minio.
        minio_user: user name for the minio instance
        minio_pwd: password for the minio instance
        num_rows: number of rows to sample from the file for analysis
        user_input_tests: tests to run on the file
        output_mode: LIMITED or ALL, whether or not to return all possible types or only the most likely one for each column

    Returns:
        dict: a dict with information about the csv and possible types for each column
    '''

    if any([location_dict is not None for location_dict in [csv_minio_location, output_minio_location, tableschema_minio_location]]) and (minio_user is None) or (minio_pwd is None):
        raise ValueError('Minio credentials are required if using Minio')

    for location_dict in [csv_minio_location, output_minio_location, tableschema_minio_location]:
        if location_dict is not None:
            if any([(location_key not in location_dict) or (location_dict[location_key] is None) for location_key in ['netloc', 'bucket', 'key']]):
                raise ValueError('Minio location dict must contain url, bucket and key')

    csv_file_path = tempfile.NamedTemporaryFile(delete=False).name
    download_from_minio(
        netloc=csv_minio_location['netloc'],
        bucket=csv_minio_location['bucket'],
        key=csv_minio_location['key'],
        filepath=csv_file_path,
        minio_user=minio_user,
        minio_pwd=minio_pwd
    )

    return_dict = routine(csv_file_path, num_rows, user_input_tests, output_mode='LIMITED', save_results=True, encoding=encoding, sep=sep)

    # Write report JSON file.
    output_path_to_store_minio_file = os.path.splitext(csv_file_path)[0] + '.json'
    with open(output_path_to_store_minio_file, 'w', encoding='utf8') as fp:
        json.dump(return_dict, fp, indent=4, separators=(',', ': '))

    upload_to_minio(
        netloc=output_minio_location['netloc'],
        bucket=output_minio_location['bucket'],
        key=output_minio_location['key'],
        filepath=output_path_to_store_minio_file,
        minio_user=minio_user,
        minio_pwd=minio_pwd
    )

    os.remove(output_path_to_store_minio_file)
    os.remove(csv_file_path)

    generate_table_schema(
        return_dict,
        netloc=tableschema_minio_location['netloc'],
        bucket=tableschema_minio_location['bucket'],
        key=tableschema_minio_location['key'],
        minio_user=minio_user,
        minio_pwd=minio_pwd
    )

    return return_dict
