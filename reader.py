import re
from mal_types import (
    make_number,
    make_symbol,
    make_string,
    make_list,
    make_vector,
    make_hashmap,
    make_keyword,
    NIL,
    TRUE,
    FALSE,
    MalException,
)


class Reader:
    def __init__(self, tokens, position=0):
        self._tokens = list(tokens)
        self._position = position
        self._iter = tokens

    def _check_position(self):
        if self._position >= len(self._tokens):
            raise MalException('EOF')

    def peek(self):
        self._check_position()
        return self._tokens[self._position]

    def next(self):
        self._check_position()
        token = self.peek()
        self._position += 1
        return token


def read_str(arg):
    tokens = tokenize(arg)
    reader = Reader(tokens)
    return read_form(reader)


def tokenize(arg):
    regex_str = r"""[\s,]*(~@|[\[\]{}()'`~^@]|"(?:\\.|[^\\"])*"?|;.*|[^\s\[\]{}('"`,;)]*)"""  # noqa
    token_regex = re.compile(regex_str)
    return [match.strip() for match in token_regex.findall(arg)]


def read_form(reader):
    curr_token = reader.peek()
    if curr_token in tuple('([{'):
        token_to_type = {
            '(': make_list,
            '[': make_vector,
            '{': make_hashmap,
        }
        sequential = token_to_type[curr_token]
        return read_list(reader, sequential)
    elif curr_token == '@':
        reader.next()
        return make_list([make_symbol('deref'), read_form(reader)])
    elif curr_token == '\'':
        reader.next()
        return make_list([make_symbol('quote'), read_form(reader)])
    elif curr_token == '`':
        reader.next()
        return make_list([make_symbol('quasiquote'), read_form(reader)])
    elif curr_token == '~':
        reader.next()
        return make_list([make_symbol('unquote'), read_form(reader)])
    elif curr_token == '~@':
        reader.next()
        return make_list([make_symbol('splice-unquote'), read_form(reader)])
    elif curr_token == '^':
        reader.next()
        term2 = read_form(reader)
        term1 = read_form(reader)
        return make_list([make_symbol('with-meta'), term1, term2])
    return read_atom(reader)


def read_list(reader, sequential):
    list_ = []
    closing_symbol = {
        '(': ')',
        '[': ']',
        '{': '}',
    }[reader.next()]
    while True:
        token = reader.peek()
        if token == closing_symbol:
            reader.next()
            return sequential(list_)
        list_.append(read_form(reader))


def valid_string(token):
    transformed = token.replace('\\\\', '').replace('\\n', '').replace('\\"', '')
    return (
        transformed.startswith('"')
        and transformed.endswith('"')
        and len(transformed) != 1
        and '\\' not in transformed
    )


def read_atom(reader):
    token = reader.next()
    if token == 'nil':
        return NIL
    elif token == 'true':
        return TRUE
    elif token == 'false':
        return FALSE
    elif re.match(r'-?\d+\.*\d*', token):
        return make_number(token)
    elif token.startswith('"'):
        if not valid_string(token):
            raise MalException('EOF')
        return make_string(token)
    elif token.startswith(':'):
        return make_keyword(token)
    elif re.match(r'.*', token):
        return make_symbol(token)
    raise MalException('Input/output error')
