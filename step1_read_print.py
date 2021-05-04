import mal_readline  # noqa: side effect import
from reader import read_str
from printer import pr_str


def READ(str_):
    return read_str(str_)


def EVAL(mal_type):
    return mal_type


def PRINT(mal_type):
    return pr_str(mal_type)


def rep(arg):
    return PRINT(EVAL(READ(arg)))


if __name__ == '__main__':
    while True:
        inp = input('user> \n')
        try:
            res = rep(inp)
            print(res)
        except Exception as e:
            print(e)
