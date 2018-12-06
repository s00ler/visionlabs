import time
import inspect
import cProfile
import functools
from collections import defaultdict


def timeit(func):
    """Measure function execution_time time."""
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = int(time.time() - start_time) * 1000
        print('{}: {} ms'.format(func.__name__, execution_time))
        return result
    return wrapped


def cache_profile(func):
    """Store function call in cache.

    Setting attr to cache_profile so i can access it later.
    Better be written as a class decorator  with __call__, etc.

    Reading from cache is required of course.
    """
    if not hasattr(cache_profile, 'CACHE'):
        setattr(cache_profile, 'CACHE', defaultdict(list))

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = int(time.time() - start_time) * 1000
        cache_profile.CACHE[func.__name__].append({
            'args': args,
            'kwargs': kwargs,
            'execution_time': execution_time
        })
        return result
    return wrapper


def profile(func):
    """Run function profile and save to file."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        spec = inspect.getargspec(func)
        if 'self' in spec.args:
            class_mod = args[0].__class__.__name__
        elif 'cls' in spec.args:
            class_mod = args[0].__name__
        else:
            class_mod = ''
        filename = '{}_{}.prof'.format(func.__name__, class_mod)

        profiler = cProfile.Profile()
        result = profiler.runcall(func, *args, **kwargs)
        profiler.dump_stats(filename)
        return result
    return wrapper
