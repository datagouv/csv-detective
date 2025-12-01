import json
from json import JSONDecodeError

proportion = 1
tags = ["type"]


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
