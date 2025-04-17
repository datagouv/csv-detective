import os
from typing import Union

# flake8: noqa
from csv_detective import detect_fields, detect_labels


def get_all_packages(detect_type) -> list:
    root_dir = os.path.dirname(os.path.abspath(__file__)) + "/" + detect_type
    modules = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            file = os.path.join(dirpath, filename).replace(root_dir, "")
            if file.endswith("__init__.py"):
                module = (
                    file.replace("__init__.py", "")
                    .replace("/", ".").replace("\\", ".")[:-1]
                )
                if module:
                    modules.append(detect_type + module)
    return modules


def return_all_tests(
    user_input_tests: Union[str, list],
    detect_type: str,
) -> list:
    """
    returns all tests that have a method _is and are listed in the user_input_tests
    the function can select a sub_package from csv_detective
    user_input_tests may look like this:
        - "ALL": all possible tests are made
        - "FR.other.siren" (or any other path-like string to one of the tests, or a group of tests, like "FR.geo"):
        this specifc (group of) test(s) only
        - ["FR.temp.mois_de_annee", "geo", ...]: only the specified tests will be made ; you may also skip
        specific (groups of) tests by add "-" at the start (e.g "-temp.date")
    """
    assert detect_type in ["detect_fields", "detect_labels"]
    all_packages = get_all_packages(detect_type=detect_type)

    if isinstance(user_input_tests, str):
        user_input_tests = [user_input_tests]
    if "ALL" in user_input_tests or all(x[0] == "-" for x in user_input_tests):
        tests_to_do = [detect_type]
    else:
        tests_to_do = [
            f"{detect_type}.{x}" for x in user_input_tests if x[0] != "-"
        ]
    tests_skipped = [
        f"{detect_type}.{x[1:]}" for x in user_input_tests if x[0] == "-"
    ]
    all_tests = [
        # this is why we need to import detect_fields/labels
        eval(x) for x in all_packages
        if any([y == x[: len(y)] for y in tests_to_do])
        and all([y != x[: len(y)] for y in tests_skipped])
    ]
    # to remove groups of tests
    all_tests = [
        test for test in all_tests if "_is" in dir(test)
    ]
    return all_tests
