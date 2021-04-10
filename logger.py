import logging


logging.basicConfig(level=logging.DEBUG)


def log_function(function):
    def wrapped_function(*args, **kwargs):
        logging.debug(f'{function.__name__} was accessed with args: {[str(arg) for arg in args]} and kwargs: {kwargs}')
        return function(*args, **kwargs)
    return wrapped_function
