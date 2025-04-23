import os
# flake8: noqa
from csv_detective import detect_fields, detect_labels
from csv_detective.load_tests import return_all_tests


def tests_conformity():
    """
    Check that all tests are properly structured:
        - an __init__.py file in the test folder
        - an _is function in the __init__.py file
    """
    for _type in ["fields", "labels"]:
        _dir = f"csv_detective/detect_{_type}"
        subfolders = []
        for dirpath, dirnames, _ in os.walk(_dir):
            for dirname in dirnames:
                if "__pycache__" not in dirname:
                    subfolders.append(os.path.join(dirpath, dirname))
        final_subfolders = [
            sf for sf in subfolders
            if not any(other_sf.startswith(sf) for other_sf in subfolders if sf != other_sf)
        ]
        for f_sf in final_subfolders:
            assert "__init__.py" in os.listdir(f_sf)
            _package = eval(
                f_sf.replace("csv_detective/", "")
                # locally we have "\\", but in CI for instance there is "/"
                .replace("\\", ".")
                .replace("/", ".")
            )
            assert "_is" in dir(_package)


def test_all_tests_have_unique_name():
    names = [t.__name__.split(".")[-1] for t in return_all_tests("ALL", "detect_fields")]
    assert len(names) == len(set(names))
