from mal_types import (
    make_symbol, make_list, is_symbol, MalException
)


VARIADIC_ASSIGNMENT_SYMBOL = make_symbol('&')


class Env:
    def __init__(self, outer=None, binds=[], exprs=[]):
        self._scope = {}
        self._outer = outer
        if (
            len(binds) != len(exprs)
            and VARIADIC_ASSIGNMENT_SYMBOL not in binds
        ):
            raise ValueError
        for idx, elem in enumerate(binds):
            if elem == VARIADIC_ASSIGNMENT_SYMBOL:
                self.set(binds[idx + 1], make_list(exprs[idx:]))
                return
            self.set(elem, exprs[idx])

    def set(self, name, value):
        self._scope[name] = value

    def find(self, name):
        if name in self._scope:
            return self
        elif self._outer is not None:
            return self._outer.find(name)
        return None

    def get(self, name):
        env = self.find(name)
        if env is None:
            if is_symbol(name):
                name = str(name, encoding='utf-8')
            raise RuntimeError(f"\"'{name}' not found\"")
        return env._scope[name]

    def __str__(self):
        str_repr = f'Definitions on this level: {tuple(self._scope)}'
        if self._outer is None:
            return str_repr
        return str_repr + '    ' + str(self._outer)
