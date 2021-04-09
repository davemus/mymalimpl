import re
from typing import Iterable, NewType, Type, List, Union, Mapping
from mal_types import MalAtom, MalList, MalVector, MalHashmap, Sequential, atoms_order


Token = NewType('Token', str)


class Reader:
    def __init__(self, tokens: Iterable[Token], position=0):
        self._tokens = list(tokens)
        self._position = position
        self._iter = tokens

    def _check_position(self):
        if self._position >= len(self._tokens):
            raise StopIteration

    def peek(self) -> Token:
        self._check_position()
        return self._tokens[self._position]

    def next(self) -> Token:
        self._check_position()
        token = self._tokens[self._position]
        self._position += 1
        return token


def read_str(arg: str) -> MalAtom:
    tokens = tokenize(arg)
    reader = Reader(tokens)
    return read_form(reader)


def tokenize(arg: str) -> Iterable[Token]:
    regex_str = """[\s,]*(~@|[\[\]{}()'`~^@]|"(?:\\.|[^\\"])*"?|;.*|[^\s\[\]{}('"`,;)]*)"""
    token_regex = re.compile(regex_str)
    return [Token(match.strip()) for match in token_regex.findall(arg)]


def read_form(reader: Reader) -> MalAtom:
    curr_token = reader.peek()
    if curr_token in '([{':
        mapping: Mapping[str, Type[Sequential]] = {'(': MalList, '[': MalVector, '{': MalHashmap}
        sequential = mapping[curr_token]
        return read_list(reader, sequential)
    return read_atom(reader)


def read_list(reader: Reader, sequential: Type[Sequential]) -> Sequential:
    list_: List[MalAtom] = []
    reader.next()  # pass ([{ symbol
    while True:
        token = reader.peek()
        if token in '])}':
            reader.next()
            return sequential(list_)
        list_.append(read_form(reader))


def read_atom(reader: Reader) -> MalAtom:
    token = reader.next()
    for atom in atoms_order:
        if atom.can_be_converted(token):
            return atom.from_mal(token)
    raise RuntimeError(f'Wrong token: {token}')
