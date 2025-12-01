from typing import Callable

from csv_detective.parsing.text import header_score


class Format:
    def __init__(
        self,
        name: str,
        func: Callable,
        _test_values: dict[bool, list[str]],
        labels: list[str] = [],
        proportion: float = 1,
        tags: list[str] = [],
    ) -> None:
        self.name: str = name
        # func is the value test for the format (returns whether a string is valid)
        self.func: Callable = func
        # _test_values are lists of valid and invalid values, used in the tests
        self._test_values: dict[bool, list[str]] = _test_values
        # labels is the list of hint headers for the header score
        self.labels: list[str] = labels
        # proportion is the tolerance (between 0 and 1) to say a column is valid for a format
        # (1 => 100% of the column has to pass the func check for the column to be considered valid)
        self.proportion: float = proportion
        # tags are to allow users to submit a file to only a subset of formats
        self.tags: list[str] = tags

    def is_valid_label(self, val: str) -> float:
        return header_score(val, self.labels)


class FormatsManager:
    formats: dict[str, Format]

    def __init__(self) -> None:
        import csv_detective.formats as formats

        format_labels = [f for f in dir(formats) if "_is" in dir(getattr(formats, f))]
        self.formats = {
            label: Format(
                name=label,
                func=(module := getattr(formats, label))._is,
                _test_values=module._test_values,
                **{
                    attr: val
                    for attr in ["labels", "proportion", "tags"]
                    if (val := getattr(module, attr, None))
                },
            )
            for label in format_labels
        }

    def get_formats_from_tags(self, tags: list[str]) -> dict[str, Format]:
        return {
            label: fmt
            for label, fmt in self.formats.items()
            if all(tag in fmt.tags for tag in tags)
        }

    def available_tags(self) -> set[str]:
        return set(tag for format in self.formats.values() for tag in format.tags)
