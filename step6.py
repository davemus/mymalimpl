#!/bin/python3

from mal_readline import mal_readline
from mal_types import MalType, MalSymbol, MalList, MalVector, MalHashmap, MalNil, MalBoolean, MalFunction, MalAtom
from reader import read_str
from printer import pr_str
from preprocessing import handle_comments, check_parens, UnmatchedParens
from core import repl_env
from errors import MalTypeError, NotFound, SpecialFormError
from functools import reduce
from env import Env


def eval_ast(ast: MalType, env: Env):
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


def READ(arg: str) -> MalType:
    return read_str(arg)


DEF_SYMBOL = MalSymbol('def!')
LET_SYMBOL = MalSymbol('let*')
IF_SYMBOL = MalSymbol('if')
DO_SYMBOL = MalSymbol('do')
FN_SYMBOL = MalSymbol('fn*')


def EVAL(ast: MalType, env: Env):
    while True:
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
            env = new_env
            ast = instructions
            continue

        # make bunch of instruction, return result of last
        elif ast.value[0] == DO_SYMBOL:
            # do syntax is (do /expression1/ ... /expressionN/)
            op, *exprs = ast.value
            for expr in exprs[:-1]:  # tco
                EVAL(expr, env)
            ast = exprs[-1]  # tco
            continue

        # if else
        elif ast.value[0] == IF_SYMBOL:
            try:
                op, mal_condition, true_branch, false_branch = ast.value
            except ValueError:
                raise SpecialFormError('if syntax is (if /condition/ /true_branch/ /false_branch/)')
            condition = EVAL(mal_condition, env)
            if condition in [MalNil(None), MalBoolean(False)]:
                ast = false_branch
            else:
                ast = true_branch
            continue

        # function construction (without binding to env)
        elif ast.value[0] == FN_SYMBOL:
            try:
                op, binds, body = ast.value
            except ValueError:
                raise SpecialFormError('fn* syntax us (fn* /arguments/ /function_body/)')

            def closure(*arguments: MalType):
                try:
                    new_env = Env(outer=env, binds=binds.value, exprs=arguments)
                except ValueError:
                    raise SpecialFormError(
                        'Error: function is called with wrong number of parameters'
                        f'expected: {len(binds.value)}, actual: {len(arguments)}'
                    )
                return EVAL(body, new_env)
            return MalFunction(body, binds, env, closure)

        # apply/invoke function
        func, *args = eval_ast(ast, env).value
        if not isinstance(func, MalFunction):
            # core function
            return func(*args)
        ast = func.ast
        env = Env(func.env, func.params, args)


def PRINT(arg) -> str:
    return pr_str(arg)


def rep(arg: str):
    return PRINT(EVAL(READ(arg), repl_env))


def eval(ast: MalType) -> MalType:
    return EVAL(ast, repl_env)


def deref(mal_type: MalType) -> MalType:
    if not isinstance(mal_type, MalAtom):
        raise MalTypeError(f'Error: {mal_type.mal_repr(True)} is not an atom')
    return mal_type.value


def reset(atom, value):
    atom.value = value
    return value


def swap(atom, fn, *args):
    if isinstance(fn, MalFunction):
        result = EVAL(fn.ast, Env(fn.env, fn.params, MalList([atom.value, *args])))
    else:
        result = fn(atom.value, *args)
    atom.value = result
    return atom.value


def setup_fns():
    repl_env.set(MalSymbol('eval'), eval)
    repl_env.set(MalSymbol('atom'), lambda arg: MalAtom(arg))
    repl_env.set(MalSymbol('atom?'), lambda arg: MalBoolean(isinstance(arg, MalAtom)))
    repl_env.set(MalSymbol('deref'), deref)
    rep('(def! load-file (fn* (f) (eval (read-string (str "(do " (slurp f) " nil)")))))')
    repl_env.set(MalSymbol('reset!'), reset)
    repl_env.set(MalSymbol('swap!'), swap)


def main():
    setup_fns()
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
