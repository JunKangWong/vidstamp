import time
import logging
from digital_card_generator import DigitalCard

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(
    "/Users/junkangwong/Documents/github_repo/digital_card/output/log/digital_video_banner.log",
    "a",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def time_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Capture the start time
        result = func(*args, **kwargs)  # Execute the function
        end_time = time.time()  # Capture the end time
        logger.info(
            f"Executing {func.__name__} took {end_time - start_time:.4f} seconds."
        )
        return result

    return wrapper


# def log_execution_time_with_details(func):
#     """
#     Decorator to log the execution time of a function along with
#     provided details (name and table number in this case).
#     """

#     def wrapper(*args, **kwargs):
#         # Extract the details
#         digital_card:DigitalCard= args[1]  # Assuming 'name' is the second positional argument
#         name=digital_card.get_name()
#         table_num=digital_card.get_table_number()
#         id=digital_card.get_id()

#         start_time = time.time()
#         result = func(*args, **kwargs)
#         end_time = time.time()
#         logger.info(
#             f"Executing {func.__name__} for id: {id}, for name: {name}, table_num: {table_num} "
#             f"took {end_time - start_time:.4f} seconds."
#         )
#         return result

#     return wrapper
