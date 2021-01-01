from time import time
from functools import wraps


def timer(func):
    """Times a function"""
    @wraps(func)
    def inner(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        print(f"Execution of {func.__name__} took {end_time - start_time} seconds")
        return result
    return inner


