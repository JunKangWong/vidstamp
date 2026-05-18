import time
import logging
from config import LOG_FILE_PATH, LAST_PROCESSED_ID_PATH

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(LOG_FILE_PATH, "a")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def time_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(
            f"Executing {func.__name__} took {end_time - start_time:.4f} seconds."
        )
        return result

    return wrapper


def log_execution_time_with_details(func):
    """
    Decorator to log the execution time of a function along with
    provided details (name and table number in this case).
    """

    def wrapper(*args, **kwargs):
        name = args[1]
        table_num = args[2]
        language = args[3]
        branch = args[4]
        id = args[5]

        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        if id is not None:
            with open(LAST_PROCESSED_ID_PATH, "w") as f:
                f.write(str(id))  # Update the ID file on success

        logger.info(
            f"Executing {func.__name__} for id: {id}, for name: {name}, table_num: {table_num}, language: {language}, branch: {branch}"
            f"took {end_time - start_time:.4f} seconds."
        )
        return result

    return wrapper
