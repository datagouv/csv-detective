import pandas as pd


def prepare_output_dict(return_table: pd.DataFrame, limited_output: bool):
    return_dict_cols = return_table.to_dict("dict")
    return_dict_cols_intermediary = {}
    for column_name in return_dict_cols:
        return_dict_cols_intermediary[column_name] = []
        for detected_value_type in return_dict_cols[column_name]:
            if return_dict_cols[column_name][detected_value_type] == 0:
                continue
            dict_tmp = {}
            dict_tmp["format"] = detected_value_type
            dict_tmp["score"] = return_dict_cols[column_name][detected_value_type]
            return_dict_cols_intermediary[column_name].append(dict_tmp)

        # Clean dict using priorities
        formats_detected = {
            x["format"] for x in return_dict_cols_intermediary[column_name]
        }
        formats_to_remove = set()
        # Deprioritise float and int detection vs others
        if len(formats_detected - {"float", "int"}) > 0:
            formats_to_remove = formats_to_remove.union({"float", "int"})
        if "int" in formats_detected:
            formats_to_remove.add("float")
        if "latitude_wgs_fr_metropole" in formats_detected:
            formats_to_remove.add("latitude_l93")
            formats_to_remove.add("latitude_wgs")
        if "longitude_wgs_fr_metropole" in formats_detected:
            formats_to_remove.add("longitude_l93")
            formats_to_remove.add("longitude_wgs")
        if "longitude_wgs" in formats_detected:
            formats_to_remove.add("longitude_l93")
        if "code_region" in formats_detected:
            formats_to_remove.add("code_departement")

        formats_to_keep = formats_detected - formats_to_remove

        detections = return_dict_cols_intermediary[column_name]
        detections = [x for x in detections if x["format"] in formats_to_keep]
        if not limited_output:
            return_dict_cols_intermediary[column_name] = detections
        else:
            return_dict_cols_intermediary[column_name] = (
                max(detections, key=lambda x: x["score"])
                if len(detections) > 0
                else {"format": "string", "score": 1.0}
            )

    return return_dict_cols_intermediary
