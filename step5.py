#!/bin/python3

from mal_readline import mal_readline
from mal_types import MalAtom, MalSymbol, MalList, MalVector, MalHashmap, MalNil, MalBoolean
from reader import read_str
from printer import pr_str, debug
from preprocessing import handle_comments, check_parens, UnmatchedParens
from core import repl_env
from errors import MalTypeError, NotFound, SpecialFormError
from functools import reduce
from env import Env
from logger import log_function


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
IF_SYMBOL = MalSymbol('if')
DO_SYMBOL = MalSymbol('do')
FN_SYMBOL = MalSymbol('fn*')


def EVAL(ast: MalAtom, env: Env):
    # not list rule of evaluation
    if not isinstance(ast, MalList):
        return eval_ast(ast, env)

    # empty list evaluates to itself
    elif not ast.value:
        return ast

    # defining things
    if ast.value[0] == DEF_SYMBOL:
        try:
            op, symbol, value = ast.value
        except ValueError:
            raise SpecialFormError('def! syntax is (def! /symbol/ /value/)')
        env.set(symbol, EVAL(value, env))
        return MalNil(None)

    # create environment with temporary bindings
    elif ast.value[0] == LET_SYMBOL:
        let_error = SpecialFormError('let* syntax is (let* /list_of definitions/ /list_of_instructions/)')
        new_env = Env(env)
        try:
            op, definitions, instructions = ast.value
        except ValueError:
            raise let_error
        if len(definitions.value) % 2 != 0:
            raise let_error
        symbol_value_pairs = list(zip(
            definitions.value[0::2],
            definitions.value[1::2]
        ))
        for symb, value in symbol_value_pairs:
            new_env.set(symb, value)
        return EVAL(instructions, new_env)

    # make bunch of instruction, return result of last
    elif ast.value[0] == DO_SYMBOL:
        # do syntax is (do /expression1/ ... /expressionN/)
        op, *exprs = ast.value
        for expr in exprs:
            result = EVAL(expr, env)
        return result

    # if else
    elif ast.value[0] == IF_SYMBOL:
        try:
            op, mal_condition, true_branch, false_branch = ast.value
        except ValueError:
            raise SpecialFormError('if syntax is (if /condition/ /true_branch/ /false_branch/)')
        condition = EVAL(mal_condition, env)
        if condition in [MalNil(None), MalBoolean(False)]:
            return EVAL(false_branch, env)
        return EVAL(true_branch, env)

    # function construction (without binding to env)
    elif ast.value[0] == FN_SYMBOL:
        try:
            op, binds, body = ast.value
        except ValueError:
            raise SpecialFormError('fn* syntax us (fn* /arguments/ /function_body/)')
        def closure(*arguments: MalAtom):
            try:
                new_env = Env(outer=env, binds=binds.value, exprs=arguments)
            except ValueError:
                raise SpecialFormError(
                    'Error: function is called with wrong number of parameters'
                    f'expected: {len(binds.value)}, actual: {len(arguments)}'
                )
            return EVAL(body, new_env)
        return closure


    # function application
    func, *args = eval_ast(ast, env).value
    return func(*args)


def PRINT(arg) -> str:
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
