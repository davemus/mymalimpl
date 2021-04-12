#!/bin/python3

from mal_readline import mal_readline
from mal_types import (
    MalAtom, MalSymbol, MalList, MalVector, MalHashmap, MalNil
)
from reader import read_str
from printer import pr_str
from preprocessing import handle_comments, check_parens, UnmatchedParens
from core import repl_env
from errors import MalTypeError, NotFound, SpecialFormError
from functools import reduce
from env import Env


def eval_ast(ast: MalAtom, env: Env):
    if isinstance(ast, MalVector):
        return MalVector([EVAL(atom, env) for atom in ast.value])
    if isinstance(ast, MalHashmap):
        return MalHashmap(
            reduce(
                lambda a, b: a + b,
                [[key, EVAL(value, env)] for key, value in ast.value.items()]
            )
        )
    if isinstance(ast, MalSymbol):
        return env.get(ast)
    elif isinstance(ast, MalList):
        return MalList([EVAL(atom, env) for atom in ast.value])
    else:
        return ast


def READ(arg: str) -> MalAtom:
    return read_str(arg)


DEF_SYMBOL = MalSymbol('def!')
LET_SYMBOL = MalSymbol('let*')


def eval_special_form(ast: MalAtom, env: Env) -> MalAtom:
    if ast.value[0] == DEF_SYMBOL:
        try:
            op, symbol, value = ast.value
        except ValueError:
            raise SpecialFormError('def! syntax is (def! /symbol/ /value/)')
        env.set(symbol, value)
        return MalNil(None)
    elif ast.value[0] == LET_SYMBOL:
        let_error = SpecialFormError('let* syntax is (let* /list_of definitions/ /list_of_instructions/)')  # noqa
        new_env = Env(env)
        try:
            op, definitions, instructions = ast.value
        except ValueError:
            raise let_error
        if len(definitions.value) % 2 != 0:
            raise let_error
        symbol_value_pairs = list(zip(
            definitions.value[0::2],
            definitions.value[1::2],
        ))
        for symb, value in symbol_value_pairs:
            new_env.set(symb, value)
        return EVAL(instructions, new_env)
    raise SpecialFormError(f'Unknown special form {ast.value[0].mal_repr()}')


def EVAL(ast: MalAtom, env: Env) -> MalAtom:
    if not isinstance(ast, MalList):
        return eval_ast(ast, env)
    elif not ast.value:
        return ast
    elif ast.value[0] in [DEF_SYMBOL, LET_SYMBOL]:
        return eval_special_form(ast, env)
    func, *args = eval_ast(ast, env).value
    return func(*args)


def PRINT(arg: MalAtom) -> str:
    return pr_str(arg)


def rep(arg: str):
    return PRINT(EVAL(READ(arg), repl_env))


def main():
    while True:
        try:
            user_input = mal_readline()
            preprocessed = handle_comments(user_input)
            check_parens(preprocessed)
            print(rep(preprocessed))
        except UnmatchedParens as e:
            print(e)
            print(user_input)
        except (MalTypeError, NotFound, SpecialFormError) as e:
            print(e)
        except (EOFError, KeyboardInterrupt):
            print()
            break


if __name__ == '__main__':
    main()
