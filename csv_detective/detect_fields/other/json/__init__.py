import json
from json import JSONDecodeError

PROPORTION = 1


def _is(val):
    '''Detects json'''
    try:
        loaded = json.loads(val)
        if isinstance(loaded, list) or (
            isinstance(loaded, dict) and not (
                any(
                    [
                        geo in loaded for geo in ['coordinates', 'geometry']
                    ]
                )
            )
        ):
            return True
        else:
            return False
    except (JSONDecodeError, TypeError):
        return False
