import time

def time_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Capture the start time
        result = func(*args, **kwargs)  # Execute the function
        end_time = time.time()  # Capture the end time
        print(f"Executing {func.__name__} took {end_time - start_time:.4f} seconds.")
        return result
    return wrapper
