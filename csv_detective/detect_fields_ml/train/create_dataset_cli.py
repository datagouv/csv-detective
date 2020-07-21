from collections import defaultdict

import pandas as pd
import re
import numpy as np
import json

def run():
    normal_types = ["commune", "departement", "region", "siret", "siren", "sexe"]
    code_types = ["postal", "departement", "region", "insee"]

    csv_data: dict = json.load(open("/home/pavel/etalab/code/csv_detective_api/csv_data_full.json"))
    type_ids = defaultdict(list)

    for id, csv in csv_data.items():
        if not "header" in csv:
            continue
        for head in csv["header"]:
            temp = head.strip('"').lower()
            if len(temp) > 20:  # We do not want too long headers
                continue
            if not temp:
                continue
            if "code" in temp:
                for code_t in code_types:
                    if re.findall(r"{}\b".format(code_t), temp):
                        type_ids[f'code_{code_t}'].append((head.replace('"', ""), id))
            else:
                for normal_t in normal_types:
                    if re.findall(r"{}\b".format(normal_t), temp):
                        type_ids[normal_t].append((head.replace('"', ""), id))


    # Now we create an annotation csv with a sample from each column:
    df_dict = defaultdict(list)
    for type_col, cols_ids in type_ids.items():
        for col, id in cols_ids:
            df_dict["columns"].append(col)
            df_dict["sample"].append(np.nan)
            df_dict["human_detected"].append(type_col)
            df_dict["csv_detected"].append(type_col)
            df_dict["id"].append(id)

    df_annotation = pd.DataFrame.from_dict(df_dict)
    df_annotation.to_csv("data/distant_annotation.csv", index=False)
    pass

if __name__ == '__main__':
    run()