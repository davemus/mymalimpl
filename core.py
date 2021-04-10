from functools import reduce, partial
from operator import add, sub, mul, truediv, eq, ge, le, gt, lt
from mal_types import MalSymbol, MalList, MalNumber, MalBoolean
from errors import MalTypeError
from env import Env

def fn_many_arg(op):
    def func(*args):
        return reduce(op, args)
    return func


def set_up_new_global_env() -> Env:
    repl_env = Env()
    repl_env.set(MalSymbol('+'), fn_many_arg(add))
    repl_env.set(MalSymbol('-'), fn_many_arg(sub))
    repl_env.set(MalSymbol('*'), fn_many_arg(mul))
    repl_env.set(MalSymbol('/'), fn_many_arg(truediv))
    repl_env.set(MalSymbol('<'), fn_many_arg(lt))
    repl_env.set(MalSymbol('>'), fn_many_arg(gt))
    repl_env.set(MalSymbol('<='), fn_many_arg(le))
    repl_env.set(MalSymbol('>='), fn_many_arg(ge))
    repl_env.set(MalSymbol('='), fn_many_arg(eq))
    repl_env.set(MalSymbol('list'), lambda *args: MalList(args))
    repl_env.set(MalSymbol('list?'), lambda *args: MalBoolean(isinstance(args[0], MalList)))
    repl_env.set(MalSymbol('count'), lambda *args: MalNumber(len(args[0])))
    repl_env.set(MalSymbol('empty?'), lambda *args: MalBoolean(len(args[0]) == 0))
    return repl_env


repl_env = set_up_new_global_env()
