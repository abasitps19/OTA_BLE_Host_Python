import asyncio
from functools import wraps

def async_to_sync(func):
    """Decorator to convert async methods to sync for existing code"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if hasattr(args[0], 'loop'):
            loop = args[0].loop
            return loop.run_until_complete(func(*args, **kwargs))
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(func(*args, **kwargs))
            finally:
                loop.close()
    return wrapper
