from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from digital_card_generator import DigitalCard
import datetime
import logging
import multiprocessing as mp
from typing import Tuple
import os
import time


## Set up logger
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


class DigitalVideoBannerGenerator:
    def __init__(self):
        # Configurations
        self.input_path = (
            "/Users/junkangwong/Documents/github_repo/digital_card/input/sample.mp4"
        )
        self.output_path = "/Users/junkangwong/Documents/github_repo/digital_card/output/digital_video_banner"
        self.codec = "libx264"
        self.audio_codec = "aac"
        self.bit_rate = "5000k"
        self.name_font_size = 54
        self.table_num_font_size = 28
        self.font_color = "black"
        self.font = "./font/BASKVILL.ttf"
        self.name_pos_x = "center"
        self.name_pos_y = -230
        self.table_num_pos_x = "center"
        self.table_num_pos_y = -176
        self.text_duration = 9.5  # TODO: derive this
        self.text_fade_duration = 1
        self.text_entrance_time = 0.5  # TODO: derive this

    def generate_name(self, name, video_size):
        name_text = TextClip(
            name,
            fontsize=self.name_font_size,
            color=self.font_color,
            font=self.font,
            size=video_size,
        )
        name_text = name_text.set_duration(self.text_duration).set_position(
            (self.name_pos_x, self.name_pos_y)
        )
        name_text = name_text.crossfadein(self.text_fade_duration)
        name_text = name_text.set_start(self.text_entrance_time)
        return name_text

    # TODO: remove one of these, they are the same, parameterize the table_num_pos except the text and some sizes.
    def generate_table_num(self, no, video_size):
        formatted_table_num = "Table No: {}".format(no)
        table_no = TextClip(
            formatted_table_num,
            fontsize=self.table_num_font_size,
            color=self.font_color,
            font=self.font,
            size=video_size,
        )
        table_no = table_no.set_duration(self.text_duration).set_position(
            (self.table_num_pos_x, self.table_num_pos_y)
        )
        table_no = table_no.crossfadein(self.text_fade_duration)
        table_no = table_no.set_start(self.text_entrance_time)
        return table_no

    def output_video(self, final_video, output_name):
        output = "{}/{}".format(self.output_path, output_name)
        final_video.write_videofile(
            output,
            codec=self.codec,
            audio_codec=self.audio_codec,  # Specify AAC audio codec
            bitrate=self.bit_rate,
        )

    def generate_output_video_name(self, name, table_num):
        return "{}_{}_{date:%Y-%m-%d_%H:%M:%S}.mp4".format(
            name, table_num, date=datetime.datetime.now()
        )

    # @time_decorator
    # def process_videos(self, digital_cards: list[DigitalCard]):
    #     with mp.Pool(4) as pool:
    #         pool.map(self.process_video, digital_cards)

    # def process_video(self, digitalCard: DigitalCard):
    #     name = digitalCard.get_name()
    #     table_num = digitalCard.get_table_number()
    #     id = digitalCard.get_id()

    #     # Each process now creates its own VideoFileClip instance
    #     with VideoFileClip(self.input_path) as input_vid:
    #         name_text = self.generate_name(name, input_vid.size)
    #         table_text = self.generate_table_num(table_num, input_vid.size)
    #         input_aud = input_vid.audio

    #         final_video = CompositeVideoClip(
    #             [input_vid, name_text, table_text], use_bgclip=True
    #         )
    #         final_video = final_video.set_audio(input_aud)

    #         output_name = self.generate_output_video_name(name, table_num)
    #         self.output_video(final_video, output_name)

    ######################

    def initialize_video_pool(
        self, num_processes: int
    ) -> list[Tuple[str, Tuple[int, int]]]:
        video_pool = []
        for i in range(num_processes):
            # Unique filename for each pre-loaded video
            temp_video_path = f"{self.input_path}_{i}.mp4"

            os.system(f"cp {self.input_path} {temp_video_path}")

            # Instead of pickling VideoFileClip, store video size (width, height)
            with VideoFileClip(temp_video_path) as input_vid:
                video_pool.append((temp_video_path, input_vid.size))

        return video_pool

    @time_decorator
    def process_videos(self, digital_cards: list[DigitalCard]):
        num_processes = 8
        video_pool = self.initialize_video_pool(num_processes)

        with mp.Pool(
            processes=num_processes,
            initializer=self.worker_init,
            initargs=(video_pool,),
        ) as pool:
            pool.map(self.process_video, digital_cards)

        # ... (Cleanup remains the same)

    def worker_init(self, video_pool):
        global global_video_pool
        global_video_pool = video_pool

    def process_video(self, digitalCard: DigitalCard):
        process_id = mp.current_process()._identity[0]  # Get process ID in the worker

        # Get the video file based on the process ID (1-based indexing)
        temp_video_path, video_size = global_video_pool[process_id - 1]

        # Open the video file within the worker process
        with VideoFileClip(temp_video_path) as input_vid:
            name = digitalCard.get_name()
            table_num = digitalCard.get_table_number()
            id = digitalCard.get_id()
            input_aud = input_vid.audio
            name_text = self.generate_name(name, video_size)
            table_text = self.generate_table_num(table_num, video_size)
            final_video = CompositeVideoClip(
                [input_vid, name_text, table_text], use_bgclip=True
            )
            final_video = final_video.set_audio(input_aud)
            output_name = self.generate_output_video_name(name, table_num)
            self.output_video(final_video, output_name)


if __name__ == "__main__":
    generator = DigitalVideoBannerGenerator()
    generator.process_video("Albert Einstein", "T3")

    # Read from excel
    # TODO: check for duplicated data from excel (Validation)
    # Length check (optional)
    # Divide the task to use multiple threads for processing to improve processing speed.
    # Compression of the output with lossless compression
