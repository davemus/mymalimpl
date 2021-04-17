import logging
from pprint import pformat
from uuid import uuid4


DEBUG = False

if DEBUG:
    logging.basicConfig(level=logging.DEBUG)


def log_function(function):
    def wrapped_function(*args, **kwargs):
        call_uuid = uuid4()
        logging.debug(f'call uuid: {call_uuid}\n{function.__name__} was accessed with args:\n{pformat([str(arg) for arg in args])} and kwargs:\n{pformat(kwargs)}\n')  # noqa
        return_value = function(*args, **kwargs)
        logging.debug(f'call uuid: {call_uuid}\n{function.__name__} returned with value\n{pformat(return_value)}\n')
        return return_value
    return wrapped_function
