from collections import defaultdict, Counter

import numpy as np
from detection import detect_encoding, detect_separator, detect_headers, parse_table
from sklearn.base import BaseEstimator, TransformerMixin


class PredictCSVColumnInfoExtractor(BaseEstimator, TransformerMixin):
    """Extract the columns from a csv into the required structures in order to use
    the trained csv_detective ML pipeline
    """

    def __init__(self, n_rows=200, n_jobs=1, csv_metadata=None, save_dataset=False):

        self.n_rows = n_rows
        self.n_jobs = n_jobs
        self.save_dataset = save_dataset
        self._file_idx = {}
        self.csv_metadata = csv_metadata

    def fit(self, X, y=None):
        return self

    def _load_file(self, file_path, n_rows):

        if self.csv_metadata is None:

            with open(file_path, mode='rb') as binary_file:
                encoding = detect_encoding(binary_file)['encoding']

            with open(file_path, 'r', encoding=encoding) as str_file:
                sep = detect_separator(str_file)

        else:
            encoding = self.csv_metadata['encoding']
            sep = self.csv_metadata['separator']

        with open(file_path, 'r', encoding=encoding) as str_file:

            try:
                table, total_lines = parse_table(
                    str_file,
                    encoding,
                    sep,
                    n_rows,
                    random_state=42
                )
            except Exception as e:
                return
        if table.empty:
            print("Could not read {}".format(file_path))
            return
        return table

    def _extract_columns(self, file_path):

        csv_df = self._load_file(file_path=file_path, n_rows=self.n_rows)

        if csv_df is None:
            return {"error": "Could not read file with pandas"}

        file_columns = []
        columns_names = []
        for j in range(len(csv_df.columns)):
            # Get all values of the column j and clean it a little bit
            temp_list = csv_df.iloc[:, j].dropna().to_list()
            file_columns.append(temp_list)
            columns_names.extend([csv_df.columns[j].lower()] * len(temp_list))

            rows_values = []

        # Get both lists of labels and values-per-column in a single flat huge list
        for i in range(csv_df.shape[1]):
            rows_values.extend(file_columns[i])

        assert len(rows_values) == len(columns_names)
        datasets_info = {"all_columns": rows_values, "all_headers": columns_names, "per_file_rows": [file_columns],
                         "headers": list(csv_df.columns)}

        return datasets_info

    def transform(self, csv_paths):

        columns_info = self._extract_columns(csv_paths)
        return columns_info


def get_column_prediction(column_series, pipeline):
    pass


def get_columns_ML_prediction(csv_path, model, csv_metadata=None, num_rows=500):
    ext = PredictCSVColumnInfoExtractor(n_rows=num_rows, csv_metadata=csv_metadata)
    csv_info = ext.transform(csv_path)
    if not csv_info:
        # logger.error("Could not read {}".format(csv_path))
        return

    y_pred = model.predict(csv_info)
    return y_pred, csv_info


def get_columns_types(y_pred, csv_info):
    def get_most_frequent(header, list_predictions):
        type_, counts = Counter(list_predictions).most_common(1)[0]
        # u, counts = np.unique(list_predictions, return_counts=True)
        # print(u, counts)
        return type_

    assert (len(y_pred) == len(csv_info["all_headers"]))
    dict_columns = defaultdict(list)
    head_pred = list(zip(csv_info["all_headers"], y_pred))
    per_header_predictions = defaultdict(list)
    for v in head_pred:
        per_header_predictions[v[0]].append(v[1])
    for header in csv_info["headers"]:
        if not per_header_predictions[header.lower()]:
            continue
        else:
            most_freq_label = get_most_frequent(header, per_header_predictions[header.lower()])
            if most_freq_label == "O":
                continue
            dict_columns[header].append(most_freq_label)
    return dict_columns

if __name__ == '__main__':
    import joblib

    pp = joblib.load("models/model.joblib")
    # y_pred, csv_info = get_columns_ML_prediction("/home/pavel/7c952230-af2f-4e42-8490-285f2abe3875.csv", pipeline=pp)
    y_pred, csv_info = get_columns_ML_prediction("/data/datagouv/csv_top/af637e2e-64cc-447f-afc4-7376be8d5eb0.csv", model=pp)
    dict_columns = get_columns_types(y_pred, csv_info)
    print(dict_columns)
