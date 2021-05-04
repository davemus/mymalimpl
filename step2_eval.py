import mal_readline  # noqa: side effect import
from reader import read_str
from printer import pr_str
from mal_types import (
    is_vector, make_vector,
    is_hashmap, make_hashmap_from_pydict, items,
    is_list, make_list, is_empty, iterate,
    is_symbol, make_symbol,
)


repl_env = {
    make_symbol('+'): lambda a, b: a + b,
    make_symbol('-'): lambda a, b: a - b,
    make_symbol('*'): lambda a, b: a * b,
    make_symbol('/'): lambda a, b: a / b
}


def eval_ast(ast, env):
    if is_vector(ast):
        return make_vector(EVAL(elem, env) for elem in iterate(ast))
    if is_hashmap(ast):
        return make_hashmap_from_pydict(
            {key: EVAL(value, env) for key, value in items(ast)}
        )
    if is_symbol(ast):
        return env.get(ast)
    elif is_list(ast):
        return make_list(EVAL(elem, env) for elem in iterate(ast))
    else:
        return ast


def READ(str_):
    return read_str(str_)


def EVAL(ast, env):
    if not is_list(ast):
        return eval_ast(ast, repl_env)
    elif is_empty(ast):
        return ast
    func, *args = iterate(eval_ast(ast, repl_env))
    return func(*args)


def PRINT(mal_type):
    return pr_str(mal_type)


def rep(arg):
    return PRINT(EVAL(READ(arg), repl_env))


if __name__ == '__main__':
    while True:
        inp = input('user> \n')
        try:
            res = rep(inp)
        except TypeError:
            print('Input/output error')
        else:
            print(res)
