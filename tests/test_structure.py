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


def test_format_parents_are_valid():
    for name, format in fmtm.formats.items():
        if format.parent is not None:
            assert format.parent in fmtm.formats, (
                f"{name}.parent={format.parent!r} is not a known format"
            )


def test_format_child_proportion_not_above_parent():
    # Convention, not a hard runtime rule: linked checks can retest the parent
    # when the child score is below the parent's proportion, and custom_proportions
    # may still diverge at runtime. This guards against surprising defaults in
    # format modules (a specialized format should not be stricter than its parent).
    for name, format in fmtm.formats.items():
        if format.parent is not None:
            parent = fmtm.formats[format.parent]
            assert format.proportion <= parent.proportion, (
                f"{name}.proportion ({format.proportion}) > "
                f"{format.parent}.proportion ({parent.proportion})"
            )


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
