#!/bin/python3

from mal_readline import mal_readline


def READ(arg: str) -> str:
    return arg


def EVAL(arg: str) -> str:
    return arg


def PRINT(arg: str) -> str:
    return arg


def rep(arg: str):
    return PRINT(EVAL(READ(arg)))


def main():
    while True:
        try:
            user_input = mal_readline()
            print(rep(user_input))
        except (EOFError, KeyboardInterrupt):
            print()
            break


if __name__ == '__main__':
    main()

