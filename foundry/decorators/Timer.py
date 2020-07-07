from time import time


class Timer:
    """Times how long a function takes to complete"""
    def __init__(self, func):
        self.function = func

    def __call__(self, *args, **kwargs):
        start_time = time()
        result = self.function(*args, **kwargs)
        end_time = time()
        print(f"Execution took {end_time - start_time} seconds")
        return result
