#!/bin/python3

from mal_readline import mal_readline
from mal_types import MalAtom
from reader import read_str
from printer import pr_str
from preprocessing import handle_comments, check_parens, UnmatchedParens


def READ(arg: str) -> MalAtom:
    return read_str(arg)


def EVAL(arg: MalAtom) -> MalAtom:
    return arg


def PRINT(arg: MalAtom) -> str:
    return pr_str(arg)


def rep(arg: str):
    return PRINT(EVAL(READ(arg)))


def main():
    while True:
        try:
            user_input = mal_readline()
            preprocessed = handle_comments(user_input)
            check_parens(preprocessed)
            print(rep(preprocessed))
        except UnmatchedParens as e:
            print(e)
            print(user_input)
        except (EOFError, KeyboardInterrupt):
            print()
            break


if __name__ == '__main__':
    main()

