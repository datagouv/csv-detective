# -*- coding: utf-8 -*-
# Import the csv_detective package
import json
from pprint import pprint

from explore_csv import routine


def sort_keys(dicto):
    return dict(sorted(dicto.items(), key=lambda x: x[0]))


def test_old_detection():
    file_path = './annuaire-de-leducation.csv'
    expected_results = sort_keys(json.load(open("baseline_result.json")))

    # Open your file and run csv_detective
    inspection_results = sort_keys(routine(file_path))
    current_result = json.dump(inspection_results, open("current_result.json", "w"))
    pprint(inspection_results)
    assert str(inspection_results) == str(expected_results)
