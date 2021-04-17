#!/bin/python3

import re
import argparse
from mal_readline import mal_readline
from mal_types import MalType, MalSymbol, MalList, MalVector, MalHashmap, MalNil, MalBoolean, MalFunction, MalAtom
from reader import read_str
from printer import pr_str
from preprocessing import handle_comments, check_parens, UnmatchedParens
from core import repl_env
from errors import MalTypeError, NotFound, SpecialFormError
from functools import reduce
from env import Env
from logger import log_function


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


# special forms
DEF_SYMBOL = MalSymbol('def!')
LET_SYMBOL = MalSymbol('let*')
IF_SYMBOL = MalSymbol('if')
DO_SYMBOL = MalSymbol('do')
FN_SYMBOL = MalSymbol('fn*')
QUOTE_SYMBOL = MalSymbol('quote')
QUASIQUOTE_SYMBOL = MalSymbol('quasiquote')
UNQUOTE_SYMBOL = MalSymbol('unquote')
SPLICE_UNQUOTE_SYMBOL = MalSymbol('splice-unquote')
DEFMACRO_SYMBOL = MalSymbol('defmacro!')

# functions
CONCAT_SYMBOL = MalSymbol('concat')
CONS_SYMBOL = MalSymbol('cons')
VEC_SYMBOL = MalSymbol('vec')


@log_function
def EVAL(ast: MalType, env: Env):
    while True:
        # not list rule of evaluation
        if not isinstance(ast, MalList):
            return eval_ast(ast, env)

        # empty list evaluates to itself
        elif not ast.value:
            return ast

        # macroexpand for macroses
        else:
            ast = macroexpand(ast, env)
            if not isinstance(ast, MalList):
                return eval_ast(ast, env)
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

        # quoting element
        elif ast.value[0] == QUOTE_SYMBOL:
            return ast.value[1]

        # quasiquoting element
        elif ast.value[0] == QUASIQUOTE_SYMBOL:
            ast = quasiquote(ast.value[1])
            continue

        elif ast.value[0] == DEFMACRO_SYMBOL:
            try:
                op, symbol, operation_ast = ast.value
                fn_sym, binds, body = operation_ast
                if fn_sym != FN_SYMBOL:
                    raise ValueError
            except ValueError:
                raise SpecialFormError('defmacro! syntax is (def! /symbol/ /function_body/)')
            fn = MalFunction(body, binds, env, None, True)  # fn.fn is set to None. Check in step 9 is it ok
            env.set(symbol, fn)
            return MalNil(None)

        # apply/invoke function
        func, *args = eval_ast(ast, env).value
        if not isinstance(func, MalFunction) and callable(func):
            # function defined in python
            return func(*args)
        ast = func.ast
        env = Env(func.env, func.params, args)


def PRINT(arg) -> str:
    return pr_str(arg)


def rep(arg: str):
    return PRINT(EVAL(READ(arg), repl_env))


def my_eval(ast: MalType) -> MalType:
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


def quasiquote(ast: MalType):
    if isinstance(ast, MalList):
        if ast.value[0] == UNQUOTE_SYMBOL:
            return ast.value[1]
        else:
            processed = MalList([])
            for elt in ast.value[::-1]:
                if isinstance(elt, MalList) and elt.value[0] == SPLICE_UNQUOTE_SYMBOL:
                    processed = MalList([CONCAT_SYMBOL, elt.value[1], processed])
                else:
                    processed = MalList([CONS_SYMBOL, quasiquote(elt), processed])
            return processed
    elif isinstance(ast, MalVector):
        return MalList([VEC_SYMBOL, ast])
    elif isinstance(ast, (MalSymbol, MalHashmap)):
        return MalList([QUOTE_SYMBOL, ast])
    return ast


def is_macro_call(ast, env):
    try:
        return (
            isinstance(ast, MalList)
            and isinstance(ast.value[0], MalSymbol)
            and env.get(ast.value[0]).is_macro
        )  # function, that is macros
    except (AttributeError, NotFound):
        return False


def macroexpand(ast, env):
    while is_macro_call(ast, env):
        fn_name, *arguments = ast.value
        macro_fn = env.get(fn_name)
        new_env = Env(macro_fn.env, macro_fn.params, MalList(arguments))
        ast = EVAL(macro_fn.ast, new_env)
    return ast


def setup_fns():
    repl_env.set(MalSymbol('eval'), my_eval)
    repl_env.set(MalSymbol('atom'), lambda arg: MalAtom(arg))
    repl_env.set(MalSymbol('atom?'), lambda arg: MalBoolean(isinstance(arg, MalAtom)))
    repl_env.set(MalSymbol('deref'), deref)
    rep('(def! load-file (fn* (f) (eval (read-string (pr-str "(do" (slurp f) "nil)")))))')
    repl_env.set(MalSymbol('reset!'), reset)
    repl_env.set(MalSymbol('swap!'), swap)


parser = argparse.ArgumentParser()
parser.add_argument('-i', '--interactive', action='store_true')
parser.add_argument('filename', nargs='?', help='Filename to be executed')
parser.add_argument('prog_args', nargs='*', help='Arguments passed to program')
args = parser.parse_args()


def preprocess_args(args):
    processed = []
    for arg in args:
        if re.match(r'\d+', arg):
            processed.append(arg)
        else:
            processed.append(f'"{arg}"')
    return processed


def main():
    setup_fns()
    if args.filename is not None:
        rep(f'(def! *FILENAME* "{args.filename}"')
        cl_args = preprocess_args(args.prog_args)
        rep(f'(def! *ARGS* {"(list " +  " ".join(cl_args) + ")" })')
        print(rep('(load-file *FILENAME*)'))
        if not args.interactive:
            return 0
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
