import re
from typing import Optional, List, Union
from errors import MalTypeError


class MalAtom:
    def __init__(self, value):
        self.value = value

    def __call__(self, *args):
        raise MalTypeError(f'{self.value} is not a function')

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


class MalNumber(MalAtom):
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


class MalString(MalAtom):
    @classmethod
    def from_mal(cls, value):
        return MalString(str(value))

    @classmethod
    def can_be_converted(cls, value):
        return re.match(r"""(".*")""", value)


class MalBoolean(MalAtom):
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
    @classmethod
    def from_mal(cls, value):
        return MalSymbol(str(value))

    @classmethod
    def can_be_converted(cls, value):
        return True

    def __hash__(self):
        return hash(self.value)


class MalNil(MalAtom):
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
    @classmethod
    def from_mal(cls, value: str):
        return MalKeyword(value)

    @classmethod
    def can_be_converted(cls, value: str):
        return value[0] == ':'

    def __hash__(self):
        return hash(self.value)


class MalList(MalAtom):
    def mal_repr(self):
        return f"({' '.join(atom.mal_repr() for atom in self.value)})"

    def __eq__(self, value):
        raise NotImplementedError


class MalVector(MalAtom):
    def mal_repr(self):
        return f"[{' '.join(atom.mal_repr() for atom in self.value)}]"

    def __eq__(self, value):
        raise NotImplementedError


class MalHashmap(MalAtom):
    def __init__(self, value: List[MalAtom]):
        self.value = dict(zip(value[0::2], value[1::2]))

    def mal_repr(self):
        list_of_elem = [f'{key.mal_repr()} {value.mal_repr()}' for key, value in self.value.items()]
        return "{" + ', '.join(list_of_elem) + "}"

    def __eq__(self, other):
        raise NotImplemented


atoms_order = [MalBoolean, MalNumber, MalNil, MalKeyword, MalString, MalSymbol]

Sequential = Union[MalList, MalVector, MalHashmap]
