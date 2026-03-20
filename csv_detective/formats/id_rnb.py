from frformat import IdRNB

proportion = 1
description = "Building identifier from the French national building reference source ([RNB](https://rnb.beta.gouv.fr/definition))"
tags = ["fr", "geo"]
mandatory_label = True
labels = {"rnb": 1, "batid": 1}

_id_rnb = IdRNB()


def _is(val) -> bool:
    return isinstance(val, str) and _id_rnb.is_valid(val)


_test_values = {
    True: ["FT4RKBXBVH9S", "NHDE2W8HE3X3"],
    False: ["FT4RKBXBVH9S1", "FT4RKBXBVH9", "NIDE2W8HE3X3", "FT4R-KBXB-VH9S", "ft4rkbxbvh9s"],
}
