from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from digital_card_generator import DigitalCard
from utility import time_decorator, log_execution_time_with_details
import datetime
import os
import concurrent.futures
import logging

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

class DigitalVideoBannerGenerator:
    def __init__(self):
        # Configurations
        self.input_path = "/Users/junkangwong/Documents/github_repo/digital_card/input/sample_vid5.mp4"
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

    @log_execution_time_with_details
    def process_video(self, name, table_num, id=None):        
        input_vid = VideoFileClip(self.input_path)
        name_text = self.generate_name(name, input_vid.size)
        table_text = self.generate_table_num(table_num, input_vid.size)
        input_aud = input_vid.audio
        final_video = CompositeVideoClip(
            [input_vid, name_text, table_text], use_bgclip=True
        )
        final_video = final_video.set_audio(input_aud)
        output_name = self.generate_output_video_name(name, table_num)
        self.output_video(final_video, output_name)
        input_vid.close()

    @time_decorator
    def process_videos(self, digital_cards: list[DigitalCard]):
        num_workers = os.cpu_count()  # Get the number of available processors
        logger.info(f"Using {num_workers} workers for processing.")

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            # Submit tasks to the executor
            futures = {
                executor.submit(
                    self.process_video,
                    card.get_name(),
                    card.get_table_number(),
                    card.get_id(),
                ): card
                for card in digital_cards
            }

            # Wait for results and handle exceptions
            for future in concurrent.futures.as_completed(futures):
                card = futures[future]
                try:
                    future.result()  # If an exception occurred during processing, it will be raised here
                except Exception as e:
                    logger.error(f"Error processing video for {card}: {e}")


if __name__ == "__main__":
    generator = DigitalVideoBannerGenerator()
    generator.process_video("Albert Einstein", "T3")

    # Read from excel
    # TODO: check for duplicated data from excel (Validation)
    # Length check (optional)
    # Divide the task to use multiple threads for processing to improve processing speed.
    # Compression of the output with lossless compression
