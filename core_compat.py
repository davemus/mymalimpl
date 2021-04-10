from functools import wraps, reduce
from operator import add, sub, mul, truediv
from mal_types import MalAtom, MalNumber, MalSymbol
from errors import MalTypeError
from env import Env


def _construct_operation(op):
    @wraps(op)
    def new_func(*args: MalAtom):
        for arg in args:
            if not isinstance(arg, MalNumber):
                raise MalTypeError(f'{arg.mal_repr()} is not a number')
        return MalNumber(reduce(op, (atom.value for atom in args)))
    return new_func


def set_up_new_global_env() -> Env:
    repl_env = Env()
    repl_env.set(MalSymbol('+'), _construct_operation(add))
    repl_env.set(MalSymbol('-'), _construct_operation(sub))
    repl_env.set(MalSymbol('*'), _construct_operation(mul))
    repl_env.set(MalSymbol('/'), _construct_operation(truediv))
    return repl_env


repl_env = set_up_new_global_env()
