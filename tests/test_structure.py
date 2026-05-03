import os

import pytest

from csv_detective import (
    routine,
    validate,
    validate_then_detect,
)
from csv_detective.format import Format, FormatsManager

fmtm = FormatsManager()


def test_all_tests_have_unique_name():
    formats: list[str] = os.listdir("csv_detective/formats")
    assert "__init__.py" in formats
    assert len(formats) == len(set(formats))


def test_conformity():
    for name, format in fmtm.formats.items():
        assert isinstance(name, str)
        assert isinstance(format, Format)
        assert all(
            getattr(format, attr) is not None
            for attr in [
                "name",
                "func",
                "_test_values",
                "labels",
                "proportion",
                "tags",
            ]
        )
        # all formats should have at least one label, for the header_score to work
        assert format.labels


@pytest.mark.parametrize(
    "tags",
    (
        ["type"],
        ["temp", "fr"],
    ),
)
def test_get_from_tags(tags):
    fmts = fmtm.get_formats_from_tags(tags)
    assert len(fmts)
    for fmt in fmts.values():
        for tag in tags:
            assert tag in fmt.tags


def test_parent_references_valid():
    for name, fmt in fmtm.formats.items():
        if fmt.parent is not None:
            assert fmt.parent in fmtm.formats, (
                f"Format '{name}' declares parent '{fmt.parent}' which does not exist"
            )


def test_true_subset_invariant():
    for name, fmt in fmtm.formats.items():
        if fmt.parent is None:
            continue
        parent = fmtm.formats[fmt.parent]
        for val in fmt._test_values[True]:
            assert parent.func(val), (
                f"'{val}' is valid for '{name}' but not for parent '{fmt.parent}'"
            )


def test_leaf_formats_excludes_parents():
    leaves = fmtm.get_leaf_formats()
    for parent_name in fmtm._children:
        assert parent_name not in leaves


def test_get_ancestors():
    ancestors = fmtm.get_ancestors("latitude_wgs_fr_metropole")
    assert ancestors == ["latitude_wgs", "float"]


@pytest.mark.parametrize(
    "func, max_pos_args",
    (
        (routine, 1),
        (validate, 2),
        (validate_then_detect, 2),
    ),
)
def test_nb_max_positional_args(func, max_pos_args):
    # checks that the main exposed function have the right number of positional arguments
    args = [None for k in range(max_pos_args + 1)]
    with pytest.raises(TypeError):
        func(*args)
