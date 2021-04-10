#!/bin/python3

from mal_readline import mal_readline
from mal_types import MalAtom, MalSymbol, MalList, MalVector, MalHashmap
from reader import read_str
from printer import pr_str, debug
from preprocessing import handle_comments, check_parens, UnmatchedParens
from core import repl_env
from env import Env
from errors import MalTypeError
from functools import reduce


def eval_ast(ast: MalAtom, env: Env):
    if isinstance(ast, MalVector):
        return MalVector([EVAL(atom) for atom in ast.value])
    if isinstance(ast, MalHashmap):
        return MalHashmap(
            reduce(
                lambda a, b: a + b,
                [[key, EVAL(value)] for key, value in ast.value.items()]
            )
        )
    if isinstance(ast, MalSymbol):
        return env.get(ast)
    elif isinstance(ast, MalList):
        return MalList([EVAL(atom) for atom in ast.value])
    else:
        return ast


def READ(arg: str) -> MalAtom:
    return read_str(arg)


def EVAL(ast: MalAtom) -> MalAtom:
    if not isinstance(ast, MalList):
        return eval_ast(ast, repl_env)
    elif not ast.value:
        return ast
    func, *args = eval_ast(ast, repl_env).value
    return func(*args)


def PRINT(arg: MalAtom) -> str:
    return pr_str(arg)


def rep(arg: str):
    return PRINT(EVAL(READ(arg)))


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
        except MalTypeError as e:
            print(e)
        except (EOFError, KeyboardInterrupt):
            print()
            break


if __name__ == '__main__':
    main()
