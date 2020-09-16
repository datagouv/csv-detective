# Import the csv_detective package
import os
import json
from pathlib import Path

from csv_detective.explore_csv import routine

# Replace by your file path
input_folder = Path() / "tests" / "data"
output_folder = Path() / 'tests' / 'output_data'

for folder in os.listdir(input_folder):
    for file in os.listdir(input_folder / folder):
        # Open your file and run csv_detective
        file_path = input_folder / folder / file
        inspection_results = routine(file_path)

        # Write your file as json
        output_folder_file = output_folder / folder
        if not output_folder_file.exists():
            os.makedirs(output_folder_file)
        output_file_path = output_folder_file / file
        with open(output_file_path.with_suffix('.json'), 'w',  encoding="utf8") as fp:
            json.dump(inspection_results, fp, indent=4, separators=(',', ': '))