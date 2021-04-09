from typing import List
from functools import wraps, reduce
from operator import add, sub, mul, truediv
from mal_types import MalAtom, MalNumber, MalSymbol
from errors import MalTypeError


def _construct_operation(op):
    @wraps(op)
    def new_func(*args: List[MalAtom]):
        for arg in args:
            if not isinstance(arg, MalNumber):
                raise MalTypeError(f'{a.mal_repr()} is not a number')
        return MalNumber(reduce(op, (atom.value for atom in args)))
    return new_func


repl_env = {
    MalSymbol('+'): _construct_operation(add),
    MalSymbol('-'): _construct_operation(sub),
    MalSymbol('*'): _construct_operation(mul),
    MalSymbol('/'): _construct_operation(truediv),
}

