import os

from csv_detective.format import Format, FormatsManager


def test_all_tests_have_unique_name():
    formats: list[str] = os.listdir("csv_detective/formats")
    assert "__init__.py" in formats
    assert len(formats) == len(set(formats))


def tests_conformity():
    fmtm = FormatsManager()
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
