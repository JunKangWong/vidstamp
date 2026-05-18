from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from card_model import DigitalCard
from logging_utils import time_decorator, log_execution_time_with_details
from config import (
    VIDEO_INPUT_PATH,
    VIDEO_OUTPUT_PATH,
    VIDEO_CODEC,
    VIDEO_AUDIO_CODEC,
    VIDEO_BITRATE,
    VIDEO_NAME_FONT_SIZE,
    VIDEO_NAME_FONT_SIZE_MEDIUM,
    VIDEO_NAME_FONT_SIZE_SMALL,
    VIDEO_NAME_LENGTH_MEDIUM_THRESHOLD,
    VIDEO_NAME_LENGTH_LONG_THRESHOLD,
    VIDEO_TABLE_FONT_SIZE,
    VIDEO_FONT_COLOR,
    FONT_PATH,
    VIDEO_NAME_POS_X,
    VIDEO_NAME_POS_Y,
    VIDEO_TABLE_POS_X,
    VIDEO_TABLE_POS_Y,
    VIDEO_TEXT_DURATION,
    VIDEO_TEXT_FADE_DURATION,
    VIDEO_TEXT_ENTRANCE_TIME,
    VIDEO_EN_FILENAME,
    VIDEO_CN_FILENAME,
)
import os


class DigitalVideoBannerGenerator:
    def __init__(self):
        self.input_path = VIDEO_INPUT_PATH
        self.output_path = VIDEO_OUTPUT_PATH
        self.codec = VIDEO_CODEC
        self.audio_codec = VIDEO_AUDIO_CODEC
        self.bit_rate = VIDEO_BITRATE
        self.name_font_size = VIDEO_NAME_FONT_SIZE
        self.table_num_font_size = VIDEO_TABLE_FONT_SIZE
        self.font_color = VIDEO_FONT_COLOR
        self.font = FONT_PATH
        self.name_pos_x = VIDEO_NAME_POS_X
        self.name_pos_y = VIDEO_NAME_POS_Y
        self.table_num_pos_x = VIDEO_TABLE_POS_X
        self.table_num_pos_y = VIDEO_TABLE_POS_Y
        self.text_duration = VIDEO_TEXT_DURATION
        self.text_fade_duration = VIDEO_TEXT_FADE_DURATION
        self.text_entrance_time = VIDEO_TEXT_ENTRANCE_TIME

    def generate_name(self, name, vid_size):
        size = len(name)
        font_size = self.name_font_size
        if size > VIDEO_NAME_LENGTH_LONG_THRESHOLD:
            font_size = VIDEO_NAME_FONT_SIZE_SMALL
        elif size > VIDEO_NAME_LENGTH_MEDIUM_THRESHOLD:
            font_size = VIDEO_NAME_FONT_SIZE_MEDIUM
        name = name.title()
        name_text = TextClip(
            name,
            fontsize=font_size,
            color=self.font_color,
            font=self.font,
            size=vid_size,
        )
        name_text = name_text.set_duration(self.text_duration).set_position(
            (self.name_pos_x, self.name_pos_y)
        )
        name_text = name_text.crossfadein(self.text_fade_duration)
        name_text = name_text.set_start(self.text_entrance_time)
        return name_text

    def generate_table_num(self, no, vid_size):
        formatted_table_num = "Table No: {}".format(no)
        table_no = TextClip(
            formatted_table_num,
            fontsize=self.table_num_font_size,
            color=self.font_color,
            font=self.font,
            size=vid_size,
        )
        table_no = table_no.set_duration(self.text_duration).set_position(
            (self.table_num_pos_x, self.table_num_pos_y)
        )
        table_no = table_no.crossfadein(self.text_fade_duration)
        table_no = table_no.set_start(self.text_entrance_time)
        return table_no

    def output_video(self, final_video, output_name, branch):
        output_path = os.path.join(self.output_path, branch)
        os.makedirs(output_path, exist_ok=True)
        output = "{}/{}".format(output_path, output_name)
        final_video.write_videofile(
            output,
            codec=self.codec,
            audio_codec=self.audio_codec,
            bitrate=self.bit_rate,
        )

    def generate_output_video_name(self, name, table_num):
        name = name.title()
        name = name.replace("\\", "")
        name = name.replace("/", "")
        return "T{}_{}.mp4".format(table_num, name)

    @log_execution_time_with_details
    def process_video(self, name, table_num, language, branch, id=None):
        filename = VIDEO_EN_FILENAME if language == "E" else VIDEO_CN_FILENAME
        input_path = os.path.join(self.input_path, filename)
        input_video = VideoFileClip(input_path)
        input_video_audio = input_video.audio
        input_video_size = input_video.size
        gen_name = self.generate_name(name, input_video_size)
        table = self.generate_table_num(table_num, input_video_size)
        final_video = CompositeVideoClip(
            [input_video, gen_name, table], use_bgclip=True
        )
        final_video = final_video.set_audio(input_video_audio)
        output_name = self.generate_output_video_name(name, table_num)
        self.output_video(final_video, output_name, branch)
        input_video.close()

    @time_decorator
    def process_videos(self, digital_cards: list[DigitalCard]):
        for card in digital_cards:
            id = card.get_id()
            name = card.get_name()
            table_no = card.get_table_number()
            language = card.get_language()
            branch = card.get_branch()
            self.process_video(name, table_no, language, branch, id)


if __name__ == "__main__":
    generator = DigitalVideoBannerGenerator()
    generator.process_video("Albert Einstein", "T3")

    # Read from excel
    # TODO: check for duplicated data from excel (Validation)
    # Length check (optional)
    # Divide the task to use multiple threads for processing to improve processing speed.
    # Compression of the output with lossless compression
