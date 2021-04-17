import re
from typing import List, Union


def not_implemented(self, other):
    raise MalTypeError(f'wrong argument type {self._type_name}')


class MalType(Exception):
    def __init__(self, value):
        self.value = value

    def __call__(self, *args):
        raise MalTypeError(f'{self.value} is not a function')

    @property
    def _type_name(self) -> str:
        raise NotImplementedError

    @classmethod
    def from_mal(cls, val: str) -> 'MalType':
        raise NotImplementedError

    @classmethod
    def can_be_converted(cls, value: str) -> bool:
        raise NotImplementedError

    def __eq__(self, other):
        if not isinstance(other, MalType):
            return MalBoolean(False)
        return MalBoolean(self.value == other.value)

    def __repr__(self):
        return f'{self.__class__.__name__}({repr(self.value)})'

    def __hash__(self):
        raise MalTypeError(f'{self.value} can\'t be used as key')

    def mal_repr(self, readable) -> str:
        return str(self.value)

    __add__ = __sub__ = __mul__ = __truediv__ = not_implemented
    __gt__ = __ge__ = __lt__ = __le__ = not_implemented
    __and__ = __or__ = not_implemented


MalTypeError = SpecialFormError = NotFound = MalType  # stub for previous steps


class MalNumber(MalType):
    _type_name = 'number'

    def __init__(self, value):
        if int(value) == float(value):
            self.value = int(value)
        else:
            self.value = value

    def __index__(self):
        return int(self.value)

    @classmethod
    def from_mal(cls, val):
        try:
            conversed = int(val)
        except ValueError:
            conversed = float(val)
        return MalNumber(conversed)

    @classmethod
    def can_be_converted(cls, value):
        return re.match(r'^\d+(\.\d*)?$', value)

    def __add__(self, other):
        if not isinstance(other, MalNumber):
            return not_implemented(self, other)
        return MalNumber(self.value + other.value)

    def __sub__(self, other):
        if not isinstance(other, MalNumber):
            return not_implemented(self, other)
        return MalNumber(self.value - other.value)

    def __mul__(self, other):
        if not isinstance(other, MalNumber):
            return not_implemented(self, other)
        return MalNumber(self.value * other.value)

    def __truediv__(self, other):
        if not isinstance(other, MalNumber):
            return not_implemented(self, other)
        return MalNumber(self.value / other.value)

    def __gt__(self, other):
        if not isinstance(other, MalNumber):
            return not_implemented(self, other)
        return MalBoolean(self.value > other.value)

    def __ge__(self, other):
        if not isinstance(other, MalNumber):
            return not_implemented(self, other)
        return MalBoolean(self.value >= other.value)

    def __lt__(self, other):
        if not isinstance(other, MalNumber):
            return not_implemented(self, other)
        return MalBoolean(self.value < other.value)

    def __le__(self, other):
        if not isinstance(other, MalNumber):
            return not_implemented(self, other)
        return MalBoolean(self.value <= other.value)


class MalString(MalType):
    _type_name = 'string'

    @classmethod
    def from_mal(cls, value):
        return MalString(str(value[1:-1]))

    @classmethod
    def can_be_converted(cls, value):
        return re.match(r"""(".*")""", value)

    def mal_repr(self, readable):
        if readable:
            return self.value
        return self.value.encode().decode('unicode-escape')

    def __hash__(self):
        return hash(self.value)


class MalBoolean(MalType):
    _type_name = 'boolean'
    _possible_reprs = {'true': True, 'false': False}
    _repr = {True: 'true', False: 'false'}

    def __bool__(self):
        return bool(self.value)

    @classmethod
    def from_mal(cls, value):
        return MalBoolean(cls._possible_reprs[value])

    @classmethod
    def can_be_converted(cls, value):
        return value in cls._possible_reprs

    def mal_repr(self, __):
        return self._repr[self.value]

    def __and__(self, other):
        return MalBoolean(self.value and other.value)

    def __or__(self, other):
        return MalBoolean(self.value or other.value)


class MalSymbol(MalType):
    _type_name = 'symbol'

    @classmethod
    def from_mal(cls, value):
        return MalSymbol(str(value))

    @classmethod
    def can_be_converted(cls, value):
        return True

    def __hash__(self):
        return hash(self.value)

    def mal_repr(self, __):
        return "'" + self.value


class MalNil(MalType):
    _type_name = 'nil'
    _nil_repr = 'nil'

    @classmethod
    def from_mal(cls, __):
        return MalNil(None)

    @classmethod
    def can_be_converted(cls, value):
        return value == cls._nil_repr

    def mal_repr(self, __):
        return self._nil_repr


class MalKeyword(MalType):
    _type_name = 'keyword'

    @classmethod
    def from_mal(cls, value: str):
        return MalKeyword(value)

    @classmethod
    def can_be_converted(cls, value: str):
        return value[0] == ':'

    def __hash__(self):
        return hash(self.value)


class MalIterable(MalType):
    def __len__(self):
        return len(self.value)

    def __contains__(self, value):
        return value in self.value

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return MalBoolean(False)
        if len(other) != len(self):
            return MalBoolean(False)
        return MalBoolean(all(
            a == b for a, b in zip(self.value, other.value)
        ))

    def __getitem__(self, idx):
        return self.value[idx]


class MalList(MalIterable):
    _type_name = 'list'

    def mal_repr(self, readable):
        return f"({' '.join(atom.mal_repr(readable) for atom in self.value)})"


class MalVector(MalIterable):
    _type_name = 'vector'

    def mal_repr(self, readable):
        return f"[{' '.join(atom.mal_repr(readable) for atom in self.value)}]"


class MalHashmap(MalType):
    _type_name = 'hashmap'

    def __init__(self, value: List[MalType]):
        self.value = dict(zip(value[0::2], value[1::2]))

    def mal_repr(self, readable):
        list_of_elem = [
            f'{key.mal_repr(readable)} {value.mal_repr(readable)}'
            for key, value in self.value.items()
        ]
        return "{" + ', '.join(list_of_elem) + "}"

    def __eq__(self, other):
        return MalBoolean(False)


atoms_order = [MalBoolean, MalNumber, MalNil, MalKeyword, MalString, MalSymbol]


class MalFunction(MalType):
    def __init__(self, ast, params, env, fn, is_macro=False):
        self.ast = ast
        self.params = params
        self.env = env
        self.fn = fn
        self.is_macro = is_macro

    def __repr__(self):
        return f'MalFunction({repr(self.ast)}, {repr(self.params)}, {repr(self.env)}, {repr(self.fn)}, {self.is_macro})' # noqa

    @classmethod
    def from_mal(cls, value):
        raise NotImplementedError

    def mal_repr(self, readability):
        if not self.is_macro:
            return '#function'
        return '#macro ' + self.ast.mal_repr(readability)


class MalAtom(MalType):
    """MalAtom is a type, that holds reference to other mal_type"""
    def __init__(self, value: MalType):
        self.value = value

    @classmethod
    def from_mal(cls, value: str):
        raise NotImplementedError

    def mal_repr(self, readability):
        return '#atom: ' + self.value.mal_repr(readability)


Sequential = Union[MalIterable, MalHashmap]
