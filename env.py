from mal_types import MalAtom, MalSymbol
from errors import NotFound


VARIADIC_ASSIGNMENT_SYMBOL = MalSymbol('&')


class Env:
    def __init__(self, outer=None, binds=[], exprs=[]):
        self._scope = {}
        self._outer = outer
        if len(binds) != len(exprs) and not VARIADIC_ASSIGNMENT_SYMBOL in binds:
            raise ValueError
        for counter in range(len(exprs)):
            if binds[counter] == VARIADIC_ASSIGNMENT_SYMBOL:
                for expr in exprs[counter:]:
                    self.set(binds[counter + 1], expr)
                return
            self.set(binds[counter], exprs[counter])

    def set(self, name: MalSymbol, mal_type):
        self._scope[name] = mal_type

    def find(self, name):
        if name in self._scope:
            return self
        elif self._outer is not None:
            return self._outer.find(name)
        return None

    def get(self, name):
        env = self.find(name)
        if env is None:
            raise NotFound(name)
        return env._scope[name]

    def __str__(self):
        level = 0
        scope = self
        while scope._outer is not None:
            scope = scope._outer
            level += 1
        return (
            f'Environment with level {level}: ' + str(self._scope)
            + (str(self._outer) if self._outer is not None else '')
        )
