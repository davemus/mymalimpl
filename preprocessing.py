from collections import deque
from typing import Deque


class UnmatchedParens(RuntimeError):
    def __str__(self):
        return f'You have an unmatched parentheses at position {super().__str__()}'  # noqa


def check_parens(arg: str):
    stack: Deque[str] = deque()
    matching = {'(': ')', '[': ']', '{': '}'}
    for (num, i) in enumerate(arg):
        if i in '([{':
            stack.append(i)
        if i in ')]}':
            try:
                if not matching[stack.pop()] == i:
                    raise UnmatchedParens(num)
            except IndexError:
                raise UnmatchedParens(num)
    if stack:
        raise UnmatchedParens(0)


def handle_comments(arg: str) -> str:
    return arg.split(';')[0].strip() or 'nil'
