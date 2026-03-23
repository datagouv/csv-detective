from typing import Any, Callable

from csv_detective.parsing.text import header_score


class Format:
    def __init__(
        self,
        name: str,
        description: str,
        func: Callable[[Any], bool],
        _test_values: dict[bool, list[str]],
        labels: dict[str, float] = {},
        proportion: float | int = 1,
        tags: list[str] = [],
        mandatory_label: bool = False,
        python_type: str = "string",
    ) -> None:
        """
        Instanciates a Format object.

        Args:
            name: the name of the format.
            descrption: a short description of the format.
            func: the value test for the format (returns whether a string is valid).
            _test_values: lists of valid and invalid values, used in the tests
            labels: the dict of hint headers and their credibilty for the header score (NB: credibility is relative witin a single format, should be used to rank the valid labels)
            proportion: the tolerance (between 0 and 1) to say a column is valid for a format. (1 => 100% of the column has to pass the func check for the column to be considered valid)
            tags: to allow users to submit a file to only a subset of formats
            mandatory_label: whether the format can only be considered if the column passes both field and label tests
            python_type: the python type related to the format (less specific, used for downstream casting)
        """
        self.name: str = name
        self.description: str = description
        self.func: Callable[[Any], bool] = func
        self._test_values: dict[bool, list[str]] = _test_values
        self.labels: dict[str, float] = labels
        self.proportion: float = self.check_proportion(proportion)
        self.tags: list[str] = tags
        self.mandatory_label: bool = mandatory_label
        self.python_type: str = python_type

    def is_valid_label(self, val: str) -> float:
        return header_score(val, self.labels)

    @classmethod
    def check_proportion(cls, proportion: float | int) -> float | int:
        if proportion <= 0 or proportion > 1:
            raise ValueError("proportion should be between 0 (excluded) and 1 (included)")
        return proportion


class FormatsManager:
    formats: dict[str, Format]

    def __init__(
        self,
        *,
        custom_proportions: float | int | dict[str, float | int] | None = None,
    ) -> None:
        import csv_detective.formats as formats

        if custom_proportions is not None and not isinstance(
            custom_proportions, (float, int, dict)
        ):
            raise ValueError(
                "custom_proportion should be None, int, float or dict[str, int | float], "
                f"got {type(custom_proportions)}"
            )
        format_labels: list[str] = [f for f in dir(formats) if "_is" in dir(getattr(formats, f))]
        if isinstance(custom_proportions, dict) and not all(
            isinstance(label, str) and isinstance(prop, (float, int)) and label in format_labels
            for label, prop in custom_proportions.items()
        ):
            raise ValueError(
                "custom_proportions as a dict should contain valid format labels as keys and floats between 0 and 1 as values"
            )
        self.formats = {
            label: Format(
                name=label,
                func=(module := getattr(formats, label))._is,
                _test_values=module._test_values,
                **{
                    attr: val
                    for attr in ["labels", "description", "tags", "mandatory_label", "python_type"]
                    if (val := getattr(module, attr, None))
                }
                | {
                    "proportion": (
                        custom_proportions
                        if isinstance(custom_proportions, (float, int))
                        else (
                            # default to the internal value if not custom
                            custom_proportions.get(label, getattr(module, "proportion", 1))
                        )
                        if isinstance(custom_proportions, dict)
                        else getattr(module, "proportion", 1)
                    )
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

    def get_formats_with_mandatory_label(self) -> dict[str, Format]:
        return {label: fmt for label, fmt in self.formats.items() if fmt.mandatory_label}

    def available_tags(self) -> set[str]:
        return set(tag for format in self.formats.values() for tag in format.tags)
