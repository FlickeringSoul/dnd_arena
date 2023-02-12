
import logging


def config_logging():
    handler = logging.StreamHandler()
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


def debug_decorator(function):
    def wrapped_function(*args, **kwargs):
        logging.debug(f'Function {function.__name__} called with args={args} and kwargs={kwargs}')
        res = function(*args, **kwargs)
        logging.debug(f'Function {function.__name__} returned with value = {res}')
        return res
    return wrapped_function