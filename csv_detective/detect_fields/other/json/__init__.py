import json
from json import JSONDecodeError

PROPORTION = 1


def _is(val):
    """Detects json"""
    try:
        loaded = json.loads(val)
        # we don't want to consider integers for instance
        return isinstance(loaded, (list, dict))
    except (JSONDecodeError, TypeError):
        return False
