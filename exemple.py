# Analysis of a batch of tabular files
import os
from csv_detective import routine

# replace with your file structure
input_folder = "analysis/source"
output_folder = "analysis/output"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for file in os.listdir(input_folder):
    file_path = f"{input_folder}/{file}"
    # open your file and run csv_detective
    inspection_results = routine(
        file_path,
        save_results=f"{output_folder}/{os.path.splitext(file)[0]}.json",
        verbose=True,  # if you want to see what's happening
    )
