from typing import List
from functools import reduce
from operator import add, sub, mul, truediv, eq, ge, le, gt, lt, and_, or_
from mal_types import (
    MalSymbol, MalList, MalNumber, MalBoolean, MalString, MalNil, MalType, MalVector
)
from env import Env
from reader import read_str


def fn_many_arg(op):
    def func(*args):
        return reduce(op, args)
    return func


def pr_defis_str(*args):
    return MalString(" ".join(arg.mal_repr(True) for arg in args))


def _str(*args):
    return MalString(r" ".join(arg.mal_repr(False) for arg in args))


def prn(*args):
    print(pr_defis_str(*args).mal_repr(True))
    return MalNil(None)


def _println(*args):
    print(_str(*args).mal_repr(False))
    return MalNil(None)


def read_defis_string(mal_str: MalString) -> MalType:
    return read_str(mal_str.value)


def slurp(filename: MalString) -> MalString:
    with open(filename.value, 'r') as f:
        return MalString(f.read().strip())


def cons(elem: MalType, list_: MalList) -> MalList:
    return MalList([elem, *list_.value])


def concat(*args: MalList) -> MalList:
    list_of_lists = [list(arg.value) for arg in args]
    list_: List[MalType] = reduce(add, list_of_lists, [])
    return MalList(list_)


def nth(iterable, idx):
    try:
        return iterable.value[idx]
    except IndexError:
        return MalNil(None)


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
    repl_env.set(
        MalSymbol('list?'),
        lambda *args: MalBoolean(isinstance(args[0], MalList))
    )
    repl_env.set(MalSymbol('count'), lambda *args: MalNumber(len(args[0])))
    repl_env.set(
        MalSymbol('empty?'),
        lambda *args: MalBoolean(len(args[0]) == 0)
    )
    repl_env.set(MalSymbol('not'), lambda arg: MalBoolean(not arg))
    repl_env.set(MalSymbol('nth'), nth)
    repl_env.set(MalSymbol('first'), lambda arg: nth(arg, MalNumber(0)))
    repl_env.set(MalSymbol('rest'), lambda arg: arg.__class__(arg.value[1:]))
    repl_env.set(MalSymbol('pr-str'), pr_defis_str)
    repl_env.set(MalSymbol('str'), _str)
    repl_env.set(MalSymbol('prn'), prn)
    repl_env.set(MalSymbol('println'), _println)
    repl_env.set(MalSymbol('read-string'), read_defis_string)
    repl_env.set(MalSymbol('slurp'), slurp)
    repl_env.set(MalSymbol('cons'), cons)
    repl_env.set(MalSymbol('concat'), concat)
    repl_env.set(MalSymbol('vec'), lambda *args: MalVector(args))
    repl_env.set(MalSymbol('and'), fn_many_arg(and_))
    repl_env.set(MalSymbol('or'), fn_many_arg(or_))
    return repl_env


repl_env = set_up_new_global_env()
