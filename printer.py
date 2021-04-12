from mal_types import MalType


def pr_str(value):
    if not isinstance(value, MalType) and callable(value):
        return '#function'
    return value.mal_repr(True)


def debug(value: MalType):
    print(repr(value))
    return value
