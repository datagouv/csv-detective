import glob

import numpy as np


def get_files(data_path, ext="csv", sample=None):
    files = glob.glob(data_path + "**/*.{}".format(ext), recursive=True)
    if sample:
        return list(np.random.choice(files, sample, replace=False))
    return files


def extract_id(file_path):
    import os
    resource_id = os.path.basename(file_path)[:-4]
    return resource_id


def header_tokenizer(x):
    import re
    return re.split(r"[\s_]]+", x)