#!/bin/python
# Thanks Sagnick for idea

from functools import wraps
from collections import namedtuple


Return = namedtuple('Return', 'result')
TailCall = namedtuple('TailCall', 'args kwargs')


def tco(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        call_result = function(*args, **kwargs)
        while isinstance(call_result, TailCall):
            call_result = function(*call_result.args, **call_result.kwargs)
        if isinstance(call_result, Return):
            return call_result.result
        else:
            raise ValueError(f'Ensure, that {function.__name__} returns only Return or TailCall')  # noqa
    return wrapped


if __name__ == '__main__':
    # a bit of tests

    def factorial_rec(n, acc=1):
        if n == 0:
            return acc
        return factorial_rec(n-1, acc * n)

    TOO_BIG_FOR_NON_TCO = 10_000

    try:
        if factorial_rec(TOO_BIG_FOR_NON_TCO):
            raise RuntimeError(f'{TOO_BIG_FOR_NON_TCO} is too small')
    except RecursionError:
        print('Non tco-optimized function failed')

    @tco
    def factorial_rec_2(n, acc=1):
        if n == 0:
            return Return(acc)
        return TailCall((n - 1, acc * n), {})

    factorial_rec_2(TOO_BIG_FOR_NON_TCO)

    print('Tco-optimized function returned')
