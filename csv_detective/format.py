from typing import Callable

from .parsing.text import header_score


class Format:
    def __init__(
        self,
        name: str,
        func: Callable,
        labels: list[str] = [],
        proportion: float = 1,
        tags: list[str] = [],
    ) -> None:
        self.name = name
        self.func = func
        self.labels = labels
        self.proportion: float = proportion
        self.tags = tags
    
    def is_valid_value(self, val: str) -> bool:
        return self.func(val)
    
    def is_valid_label(self, val: str) -> float:
        return header_score(val, self.labels)


class FormatsManager:
    def __init__(self) -> None:
        import csv_detective.formats as formats
        format_labels = [
            f for f in dir(formats)
            if "_is" in dir(getattr(formats, f))
        ]
        assert len(format_labels) == len(set(format_labels)), "Format labels must be unique"
        self.formats = [
            Format(
                name=label,
                func=(module := getattr(formats, label))._is,
                **{
                    attr: val
                    for attr in ["labels", "proportion", "tags"]
                    if (val := getattr(module, attr, None))
                },
            )
            for label in format_labels
        ]
    
    def get_formats_from_tags(self, tags: list[str]) -> list[Format]:
        return [f for f in self.formats if all(tag in f.tags for tag in tags)]
