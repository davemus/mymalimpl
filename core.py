from copy import copy
from time import time
from operator import (
    add, sub, mul, truediv, lt, le, gt, ge
)
from printer import pr_str
from reader import read_str
from mal_types import (
    make_list, is_list, NIL, is_empty, count,
    is_iterable, make_symbol, is_symbol,
    make_atom, is_atom, deref, swap, reset,
    cons, concat, make_vector, is_vector, make_vector_vargs,
    first, rest, nth,
    is_nil, is_true, is_false, make_keyword, is_keyword,
    is_hashmap, keys, values, contains, get,
    make_hashmap_vargs, assoc, dissoc, make_string,
    is_string, is_function, is_number, is_mal_function,
    make_hashmap_from_pydict, make_number, can_have_metadata,
)


def prn(*args):
    print(" ".join(pr_str(arg, True) for arg in args))
    return NIL


def println(*args):
    print(" ".join(pr_str(arg, False) for arg in args))
    return NIL


def pr_str_(*args):
    string = " ".join(pr_str(arg, True) for arg in args)
    return string


def str_(*args):
    string = "".join(pr_str(arg, False) for arg in args)
    return string


def equal(op1, op2):
    if is_iterable(op1) and is_iterable(op2):  # list and vector are equal in tests =(
        if count(op1) != count(op2):
            return False
        return all(
            equal(el1, el2) for (el1, el2) in zip(op1, op2)
        )
    if is_hashmap(op1) and is_hashmap(op2):
        if set(keys(op1)) != set(keys(op2)):
            return False
        return all(equal(op1[key], op2[key]) for key in keys(op1))
    return type(op1) == type(op2) and op1 == op2


def slurp(filename):
    strip_comments = lambda line: line.split(';')[0]
    with open(filename) as f:
        contents = ' '.join(strip_comments(line) for line in f if line)
    return contents


def mal_readline(prompt):
    try:
        return input(prompt)
    except EOFError:
        return NIL


def seq(entity):
    if (
        (is_iterable(entity) or is_string(entity))
        and len(entity)
    ):
        return make_list(entity)
    return NIL


def conj(collection, *args):
    if is_list(collection):
        return make_list([*reversed(args), *collection])
    if is_vector(collection):
        return make_vector([*collection, *args])
    raise TypeError('conj element 1 should be a collection')


def py_eval(expression):
    result = eval(expression)
    if isinstance(result, (tuple, list)):
        return make_list(result)
    elif isinstance(result, str):
        return result
    elif isinstance(result, bool):
        return result
    elif isinstance(result, dict):
        return make_hashmap_from_pydict(result)
    elif isinstance(result, (int, float)):
        return make_number(result)
    elif result is None:
        return NIL
    raise TypeError(f'Can\'t convert python type {type(result)} to mal type')


def meta(element):
    if not can_have_metadata(element):
        raise TypeError(f'Type {type(element)} can\'t have meta')
    try:
        return element.meta
    except AttributeError:
        return NIL


def with_meta(target, metadata):
    if not can_have_metadata(target):
        raise TypeError(f'Type {type(target)} can\'t have meta')
    target_copy = copy(target)
    try:
        target_copy.meta = metadata
    except AttributeError:
        return target
    else:
        return target_copy


namespace_ = {
    '+': add,
    '-': sub,
    '*': mul,
    '/': truediv,
    '<': lt,
    '<=': le,
    '>': gt,
    '>=': ge,
    '=': equal,
    'list': lambda *args: make_list(args),
    'list?': is_list,
    'prn': prn,
    'println': println,
    'pr-str': pr_str_,
    'str': str_,
    'empty?': is_empty,
    'count': count,
    'read-string': read_str,
    'slurp': slurp,
    'atom': make_atom,
    'atom?': is_atom,
    'deref': deref,
    'swap!': swap,
    'reset!': reset,
    'cons': cons,
    'concat': concat,
    'vec': make_vector,
    'first': first,
    'rest': rest,
    'nth': nth,
    'nil?': is_nil,
    'true?': is_true,
    'false?': is_false,
    'symbol': make_symbol,
    'symbol?': is_symbol,
    'keyword': make_keyword,
    'keyword?': is_keyword,
    'vector': make_vector_vargs,
    'vector?': is_vector,
    'sequential?': is_iterable,
    'hash-map': make_hashmap_vargs,
    'map?': is_hashmap,
    'get': get,
    'keys': keys,
    'vals': values,
    'contains?': contains,
    'assoc': assoc,
    'dissoc': dissoc,
    'readline': mal_readline,
    '*host-language*': make_string("\"python-by-davemus\""),
    'time-ms': lambda: time() / 1000,
    # metadata is not supported in my mal implementation
    'meta': meta,
    'with-meta': with_meta,
    'fn?': lambda entity: is_function(entity) or (is_mal_function(entity) and not entity.is_macro),
    'macro?': lambda entity: is_mal_function(entity) and entity.is_macro,
    'string?': is_string,
    'number?': is_number,
    'seq': seq,
    'conj': conj,
    'py-eval': py_eval,
}

namespace = {make_symbol(k): v for k, v in namespace_.items()}
