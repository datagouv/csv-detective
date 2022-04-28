"""
Ce script analyse les premières lignes d'un CSV pour essayer de déterminer le
contenu possible des champs
"""

import json
import os
from pkg_resources import resource_string

from csv_detective import detect_fields
from csv_detective import detect_labels
from csv_detective.s3_utils import download_from_minio, upload_to_minio
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


def routine(file_path, minio_url=None, minio_bucket=None, minio_key=None, num_rows=50, user_input_tests='ALL',output_mode='LIMITED', save_results=True, upload_results=False, minio_user: str=None, minio_pwd: str=None):
    '''Returns a dict with information about the csv table and possible
    column contents.
    In order to run it with Minio, env variables MINIO_USER and MINIO_PASSWORD must be set.
    '''
    use_minio = (minio_url is not None) and (minio_bucket is not None) and (minio_key is not None)
    if use_minio:
        download_from_minio(url=minio_url, bucket=minio_bucket, key=minio_key, filepath=file_path, minio_user=minio_user, minio_pwd=minio_pwd)

    binary_file = open(file_path, mode='rb')
    encoding = detect_encoding(binary_file)['encoding']

    with open(file_path, 'r', encoding=encoding) as str_file:
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

    # Perform a mean of the two results
    # The fill_value=0 ensures that if there was no corresponding \
    #   test for labels and fields, then the overall result is divided by 2 as we are less "sure" that the field is this type
    return_table = 0.5*return_table_fields.add(return_table_labels, fill_value=0)
    return_dict_cols = prepare_output_dict(return_table, output_mode)
    return_dict['columns'] = return_dict_cols

    metier_to_python_type = {
        'booleen': 'bool',
        'ints': 'int',
        'floats': 'float',
        'string': 'str',
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
            return_dict[detection_method] = {col_name: [{'python_type': metier_to_python_type.get(detection['type'], 'str'), **detection} for detection in detections] for col_name, detections in return_dict[detection_method].items()}
    if output_mode == 'LIMITED':
        for detection_method in ['columns_fields', 'columns_labels', 'columns']:
            return_dict[detection_method] = {col_name: {'python_type': metier_to_python_type.get(detection['type'], 'str'), **detection} for col_name, detection in return_dict[detection_method].items()}

    if save_results or upload_results:
        # Write your file as json
        output_file_path = os.path.splitext(file_path)[0] + f'_{output_mode}.json'
        with open(output_file_path, 'w', encoding='utf8') as fp:
            json.dump(return_dict, fp, indent=4, separators=(',', ': '))

    if upload_results:
        output_minio_key = minio_key.replace('.csv', f'_{output_mode}.json') if minio_key.endswith('.csv') else minio_key + f'_{output_mode}.json'
        upload_to_minio(url=minio_url, bucket=minio_bucket, key=output_minio_key, filepath=output_file_path, minio_user=minio_user, minio_pwd=minio_pwd)
        if not save_results:
            os.unlink(output_file_path)

    if use_minio:
        os.remove(file_path)

    return return_dict
