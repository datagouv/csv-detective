import json
from json import JSONDecodeError

proportion = 1
python_type = "json"
tags = ["type"]
labels = {
    "list": 1,
    "dict": 1,
    "complex": 1,
}


def _is(val):
    try:
        loaded = json.loads(val)
        # we don't want to consider integers for instance
        return isinstance(loaded, (list, dict))
    except (JSONDecodeError, TypeError):
        return False


_test_values = {
    True: ['{"pomme": "fruit", "reponse": 42}', "[1,2,3,4]"],
    False: ["5", '{"zefib":', '{"a"}'],
}
