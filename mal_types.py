from copy import copy

# atomic types
NIL = None
is_nil = lambda entity: entity is NIL

TRUE = True
FALSE = False
is_bool = lambda entity: isinstance(entity, bool)
is_true = lambda entity: entity is TRUE
is_false = lambda entity: entity is FALSE


def make_number(str_):
    try:
        if float(str_) != int(str_):
            return float(str_)
        return int(str_)
    except Exception:
        return float(str_)
is_number = lambda entity: isinstance(entity, (int, float)) and not is_bool(entity)

make_keyword = lambda str_: str_ if is_keyword(str_) else u"\u029e" + str(str_.lstrip(':'))
is_keyword = lambda entity: isinstance(entity, str) and entity.startswith(u"\u029e")

def make_string(str_):  # noqa
    return (
        str_[1:-1]
        .replace('\\\\', u'\u029e')
        .replace('\\n', '\n')
        .replace('\\"', '"')
        .replace(u'\u029e', '\\')
    )
is_string = lambda entity: isinstance(entity, str) and not is_keyword(entity)  # noqa

make_symbol = lambda str_: bytes(str_, encoding='utf-8')
is_symbol = lambda entity: isinstance(entity, bytes)


class MalWithMetaMixin:
    meta = NIL
can_have_metadata = lambda entity: isinstance(entity, MalWithMetaMixin) or is_function(entity)  # noqa


# compound types
class MalList(list, MalWithMetaMixin): pass  # noqa
make_list = lambda entity: MalList(entity)  # noqa
is_list = lambda entity: isinstance(entity, MalList) and not is_atom(entity)

class MalVector(tuple, MalWithMetaMixin): pass  # noqa
make_vector = lambda entity: MalVector(entity)  # noqa
make_vector_vargs = lambda *args: make_vector(args)
is_vector = lambda entity: isinstance(entity, MalVector)

class MalHashmap(dict, MalWithMetaMixin): pass  # noqa
make_hashmap = lambda iterable: MalHashmap(zip(iterable[0::2], iterable[1::2]))  # noqa
make_hashmap_vargs = lambda *args: make_hashmap(args)
make_hashmap_from_pydict = lambda x: MalHashmap(x)
is_hashmap = lambda entity: isinstance(entity, MalHashmap)
keys = lambda entity: make_list(entity.keys())
values = lambda entity: make_list(entity.values())
get = lambda entity, key: entity.get(key, NIL) if is_hashmap(entity) else NIL
contains = lambda hashmap, key: key in hashmap.keys()
def assoc(hashmap, *items):  # noqa
    return make_hashmap_from_pydict({**hashmap, **{k: v for k, v in zip(items[0::2], items[1::2])}})
def dissoc(hashmap, *items):  # noqa
    return make_hashmap_from_pydict({k: v for k, v in hashmap.items() if k not in items})


class function(MalWithMetaMixin):
    __slots__ = ['ast', 'params', 'env', 'fn', 'is_macro', 'meta']

    def __copy__(self):
        copy_fn = function(
            copy(self.ast),
            copy(self.params),
            copy(self.env),
            copy(self.fn),
            copy(self.is_macro),
        )
        copy_fn.meta = copy(self.meta)
        return copy_fn

    def __init__(self, ast, params, env, fn, is_macro=False):
        self.ast = ast
        self.params = params
        self.env = env
        self.fn = fn
        self.is_macro = is_macro
        self.meta = NIL
make_function = function  # noqa
is_mal_function = lambda entity: isinstance(entity, function)
is_function = lambda entity: callable(entity) or is_mal_function(entity)

_atom_mark = 'atom'
atom = lambda value: make_list([_atom_mark, value])
make_atom = atom
is_atom = lambda entity: isinstance(entity, list) and len(entity) == 2 and entity[0] == _atom_mark


def deref(entity):
    if is_atom(entity):
        return entity[1]
    return NIL


def reset(entity, value):
    if is_atom(entity):
        entity[1] = value
        return value
    return NIL


def swap(entity, fn, *args):
    if not is_atom(entity):
        raise TypeError('swap! first argument should be atom')
    if is_mal_function(fn):
        fn = fn.fn
    new_value = fn(entity[1], *args)
    entity[1] = new_value
    return new_value


def items(entity):
    if is_hashmap(entity):
        return entity.items()
    raise TypeError


is_iterable = lambda entity: any(is_a(entity) for is_a in (is_list, is_vector))


def is_empty(entity):
    if is_iterable(entity):
        return not entity
    raise TypeError


def iterate(entity):
    if is_iterable(entity):
        return entity
    raise TypeError


def first(entity):
    if is_iterable(entity) and entity:
        return entity[0]
    return NIL


def rest(entity):
    if is_iterable(entity) and entity:
        return make_list(entity[1:])
    return make_list([])


def nth(entity, n):
    if is_iterable(entity):
        try:
            return entity[n]
        except IndexError:
            raise MalException('Index is beyond bounds')
    return NIL


def count(entity):
    if is_iterable(entity):
        return len(entity)
    return 0


def cons(element, sequence):
    return make_list([element, *sequence])


def concat(*sequences):
    joined = []
    for sequence in sequences:
        joined += sequence
    return make_list(joined)


def init_save_value(self, value):
    self.value = value
MalException = type('MalException', (Exception,), {'__init__': init_save_value})  # noqa
