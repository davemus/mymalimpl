import re
from typing import Optional, List, Union
from errors import MalTypeError

def not_implemented(self, other):
    raise MalTypeError(f'Error: wrong argument type {self._type_name}')


class MalAtom:
    def __init__(self, value):
        self.value = value

    def __call__(self, *args):
        raise MalTypeError(f'{self.value} is not a function')

    @property
    def _type_name(self):
        raise NotImplementedError

    @classmethod
    def from_mal(cls, val) -> 'MalAtom':
        raise NotImplementedError

    @classmethod
    def can_be_converted(cls, value: str) -> bool:
        raise NotImplementedError

    def __eq__(self, other):
        if not isinstance(other, MalAtom):
            return False
        return self.value == other.value

    def __repr__(self):
        return f'{self.__class__.__name__}({repr(self.value)})'

    def __hash__(self):
        raise MalTypeError(f'{self.value} can\'t be used as key')

    def mal_repr(self) -> str:
        return str(self.value)

    __add__ = __sub__ = __mul__ = __truediv__ = not_implemented
    __gt__ = __ge__ = __lt__ = __le__ = not_implemented


class MalNumber(MalAtom):
    _type_name = 'number'

    def __init__(self, value):
        if int(value) == float(value):
            self.value = int(value)
        else:
            self.value = value

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

    def __lte__(self, other):
        if not isinstance(other, MalNumber):
            return not_implemented(self, other)
        return MalBoolen(self.value <= other.value)


class MalString(MalAtom):
    _type_name = 'string'

    @classmethod
    def from_mal(cls, value):
        return MalString(str(value))

    @classmethod
    def can_be_converted(cls, value):
        return re.match(r"""(".*")""", value)


class MalBoolean(MalAtom):
    _type_name = 'boolean'
    _possible_reprs = {'true': True, 'false': False}
    _repr = {True: 'true', False: 'false'}

    @classmethod
    def from_mal(cls, value):
        return MalBoolean(cls._possible_reprs[value])

    @classmethod
    def can_be_converted(cls, value):
        return value in cls._possible_reprs

    def mal_repr(self):
        return self._repr[self.value]


class MalSymbol(MalAtom):
    _type_name = 'symbol'

    @classmethod
    def from_mal(cls, value):
        return MalSymbol(str(value))

    @classmethod
    def can_be_converted(cls, value):
        return True

    def __hash__(self):
        return hash(self.value)


class MalNil(MalAtom):
    _type_name = 'nil'
    _nil_repr = 'nil'

    @classmethod
    def from_mal(cls, __):
        return MalNil(None)

    @classmethod
    def can_be_converted(cls, value):
        return value == cls._nil_repr

    def mal_repr(self):
        return self._nil_repr


class MalKeyword(MalAtom):
    _type_name = 'keyword'

    @classmethod
    def from_mal(cls, value: str):
        return MalKeyword(value)

    @classmethod
    def can_be_converted(cls, value: str):
        return value[0] == ':'

    def __hash__(self):
        return hash(self.value)


class MalList(MalAtom):
    _type_name = 'list'

    def mal_repr(self):
        return f"({' '.join(atom.mal_repr() for atom in self.value)})"

    def __eq__(self, value):
        return False


class MalVector(MalAtom):
    _type_name = 'vector'

    def mal_repr(self):
        return f"[{' '.join(atom.mal_repr() for atom in self.value)}]"

    def __eq__(self, value):
        return False


class MalHashmap(MalAtom):
    _type_name = 'hashmap'

    def __init__(self, value: List[MalAtom]):
        self.value = dict(zip(value[0::2], value[1::2]))

    def mal_repr(self):
        list_of_elem = [f'{key.mal_repr()} {value.mal_repr()}' for key, value in self.value.items()]
        return "{" + ', '.join(list_of_elem) + "}"

    def __eq__(self, other):
        return False


atoms_order = [MalBoolean, MalNumber, MalNil, MalKeyword, MalString, MalSymbol]

Sequential = Union[MalList, MalVector, MalHashmap]
