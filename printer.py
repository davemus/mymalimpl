from mal_types import MalAtom


def pr_str(value: MalAtom):
    return value.mal_repr()


def debug(value: MalAtom):
    return repr(value)
