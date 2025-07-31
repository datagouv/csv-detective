import pandas as pd


def prepare_output_dict(return_table: pd.DataFrame, limited_output: bool):
    # -> dict[str, dict | list[dict]] (to be added when upgrading to python>=3.10)
    return_dict_cols = return_table.to_dict("dict")
    output_dict = {}
    for column_name in return_dict_cols:
        # keep only formats with a non-zero score
        output_dict[column_name] = [
            {
                "format": detected_value_type,
                "score": return_dict_cols[column_name][detected_value_type],
            }
            for detected_value_type in return_dict_cols[column_name]
            if return_dict_cols[column_name][detected_value_type] > 0
        ]
        priorities = [
            # no need to specify int and float everywhere, they are deprioritized anyway
            ("int", ("float",)),
            # bool over everything
            (
                "booleen",
                (
                    "latitude_l93",
                    "latitude_wgs",
                    "latitude_wgs_fr_metropole",
                    "longitude_l93",
                    "longitude_wgs",
                    "longitude_wgs_fr_metropole",
                ),
            ),
            ("geojson", ("json",)),
            # latlon over lonlat if no longitude allows to discriminate
            ("latlon_wgs", ("json", "lonlat_wgs")),
            ("lonlat_wgs", ("json",)),
            ("latitude_wgs_fr_metropole", ("latitude_l93", "latitude_wgs")),
            ("longitude_wgs_fr_metropole", ("longitude_l93", "longitude_wgs")),
            ("latitude_wgs", ("latitude_l93",)),
            ("longitude_wgs", ("longitude_l93",)),
            ("code_region", ("code_departement",)),
            ("datetime_rfc822", ("datetime_aware",)),
        ]
        detected_formats = set(x["format"] for x in output_dict[column_name])
        formats_to_remove = set()
        # Deprioritise float and int detection vs others
        if len(detected_formats - {"float", "int"}) > 0:
            formats_to_remove = formats_to_remove.union({"float", "int"})
        # Deprioritize less specific formats if:
        # secondary score is even or worse
        # or priority score is at least 1 (max of the field score)
        for prio_format, secondary_formats in priorities:
            if prio_format in detected_formats:
                for secondary in secondary_formats:
                    if secondary in detected_formats and (
                        return_dict_cols[column_name][prio_format]
                        >= return_dict_cols[column_name][secondary]
                        or return_dict_cols[column_name][prio_format] >= 1
                    ):
                        formats_to_remove.add(secondary)

        formats_to_keep = detected_formats - formats_to_remove

        detections = [x for x in output_dict[column_name] if x["format"] in formats_to_keep]
        if not limited_output:
            output_dict[column_name] = detections
        else:
            output_dict[column_name] = (
                max(detections, key=lambda x: x["score"])
                if len(detections) > 0
                else {"format": "string", "score": 1.0}
            )

    return output_dict
