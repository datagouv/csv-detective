'''Loads an annotated file and extracts features and tagged types for each resource id

Usage:
    split_dataset_train_test.py <i> <tr> [options]

Arguments:
    <i>                                Input annotation file to split
    <tr>                 Percentage for training . If 1.0, then no testing split is created [default: 0.7:float]
'''


import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit
from argopt import argopt
import numpy as np
import os

if __name__ == '__main__':
    parser = argopt(__doc__).parse_args()
    annotation_file_path = parser.i
    training_size = parser.tr

    annotation_folder = os.path.dirname(annotation_file_path)

    if training_size == 1.0 or training_size == 0.0:
        print("Enter a valid 0<value<1")

    df = pd.read_csv(annotation_file_path)
    y = df["human_detected"].fillna("O").values

    sss = StratifiedShuffleSplit(n_splits=1, train_size=training_size, random_state=42)
    train, test = next(sss.split(np.zeros(len(y)), y))

    # Save the datasets

    ## Training
    df_train: pd.DataFrame = df.loc[train, :]
    df_train.to_csv(f"{annotation_folder}/train.csv", header=True, index=False)

    ## Test
    df_test: pd.DataFrame = df.loc[test, :]
    df_test.to_csv(f"{annotation_folder}/test.csv", header=True, index=False)
