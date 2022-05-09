"""
Ce script analyse les premières lignes d'un CSV pour essayer de déterminer le
contenu possible des champs
"""

import json
from multiprocessing.sharedctypes import Value
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


def routine(csv_file_path=None, minio_url=None, minio_user: str=None, minio_pwd: str=None, minio_bucket=None, minio_key=None, num_rows=50, user_input_tests='ALL',output_mode='LIMITED', save_results=True, upload_results=False, save_tableschema=False):
    '''Returns a dict with information about the csv table and possible
    column contents.

    Args:
        csv_file_path (str): local path to CSV file if not using Minio
        minio_url (str): url of the minio instance
        minio_user (str): user name for the minio instance
        minio_pwd (str): password for the minio instance
        minio_bucket (str): bucket to download the file from
        minio_key (str): key of the CSV file to download from the minio instance
        num_rows (int): number of rows to sample from the file for analysis
        user_input_tests (str or list): tests to run on the file
        output_mode (str): LIMITED or ALL, whether or not to return all possible types or only the most likely one for each column
        save_results (bool): whether or not to save the results in a json file
        upload_results (bool): whether or not to upload the results to minio
        save_tableschema (bool): whether or not to save the tableschema in a json file on the minio instance

    Returns:
        dict: a dict with information about the csv and possible types for each column
    '''
    use_minio = not any(param is None for param in [minio_url, minio_bucket, minio_key, minio_user, minio_pwd])
    if use_minio:
        if csv_file_path is not None:
            raise ValueError('You can either use a Minio instance or a local file, not both')
        csv_file_path = tempfile.NamedTemporaryFile(delete=False).name
        download_from_minio(url=minio_url, bucket=minio_bucket, key=minio_key, filepath=csv_file_path, minio_user=minio_user, minio_pwd=minio_pwd)
    elif csv_file_path is None:
            raise ValueError('file_path is required if not using minio')


    binary_file = open(csv_file_path, mode='rb')
    encoding = detect_encoding(binary_file)['encoding']

    with open(csv_file_path, 'r', encoding=encoding) as str_file:
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

    if save_results or upload_results:
        # Write your file as json
        output_path_to_store_minio_file = os.path.splitext(csv_file_path)[0] + f'_{output_mode}.json'
        with open(output_path_to_store_minio_file, 'w', encoding='utf8') as fp:
            json.dump(return_dict, fp, indent=4, separators=(',', ': '))

    if upload_results:
        output_minio_key = minio_key.replace('.csv', f'_{output_mode}.json') if minio_key.endswith('.csv') else minio_key + f'_{output_mode}.json'
        upload_to_minio(url=minio_url, bucket=minio_bucket, key=output_minio_key, filepath=output_path_to_store_minio_file, minio_user=minio_user, minio_pwd=minio_pwd)
        if not save_results:
            os.unlink(output_path_to_store_minio_file)

    if use_minio:
        os.remove(csv_file_path)

    if save_tableschema:
        if output_mode == 'ALL':
            raise ValueError('Saving tableschema for ALL output mode is not supported.')
        generate_table_schema(return_dict, url=minio_url, bucket="tableschema", key=minio_key, minio_user=minio_user, minio_pwd=minio_pwd)

    return return_dict
