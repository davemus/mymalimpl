class MalTypeError(TypeError):
    def __str__(self):
        return f'Error: {super().__str__()}'


class NotFound(RuntimeError):
    def __str__(self):
        return f'Error: {super().__str__()} is not defined'


class SpecialFormError(RuntimeError):
    pass
