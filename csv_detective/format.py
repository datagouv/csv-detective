from typing import Any, Callable

from csv_detective.parsing.text import header_score


class Format:
    def __init__(
        self,
        name: str,
        func: Callable[[Any], bool],
        _test_values: dict[bool, list[str]],
        labels: list[str] = [],
        proportion: float = 1,
        tags: list[str] = [],
    ) -> None:
        """
        Instanciates a Format object.

        Args:
            name: the name of the format.
            func: the value test for the format (returns whether a string is valid).
            _test_values: lists of valid and invalid values, used in the tests
            labels: the list of hint headers for the header score
            proportion: the tolerance (between 0 and 1) to say a column is valid for a format. (1 => 100% of the column has to pass the func check for the column to be considered valid)
            tags: to allow users to submit a file to only a subset of formats
        """
        self.name: str = name
        self.func: Callable = func
        self._test_values: dict[bool, list[str]] = _test_values
        self.labels: list[str] = labels
        self.proportion: float = proportion
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
