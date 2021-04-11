from mal_types import MalAtom


def pr_str(value):
    if not isinstance(value, MalAtom) and callable(value):
        return '#function'
    return value.mal_repr(True)


def debug(value: MalAtom):
    print(repr(value))
    return value
