import mal_readline


def READ(arg):
    return arg


def EVAL(arg):
    return arg


def PRINT(arg):
    return arg


def rep(arg):
    return PRINT(EVAL(READ(arg)))


if __name__ == '__main__':
    while True:
        inp = input('user> \n')
        res = rep(inp)
