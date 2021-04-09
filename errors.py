class MalTypeError(TypeError):
    def __str__(self):
        return f'Error: {super().__str__()}'

