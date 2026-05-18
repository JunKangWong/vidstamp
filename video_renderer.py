from moviepy import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.fx import CrossFadeIn
from PIL import ImageFont
from card_model import DigitalCard
from logging_utils import time_decorator, log_execution_time_with_details
from config import (
    VIDEO_INPUT_PATH,
    VIDEO_OUTPUT_PATH,
    VIDEO_CODEC,
    VIDEO_AUDIO_CODEC,
    VIDEO_BITRATE,
    VIDEO_NAME_FONT_SIZE,
    VIDEO_NAME_FONT_SIZE_MIN,
    VIDEO_NAME_FONT_SIZE_STEP,
    VIDEO_NAME_MAX_WIDTH,
    VIDEO_NAME_CASING,
    VIDEO_TABLE_FONT_SIZE,
    VIDEO_TABLE_PREFIX,
    VIDEO_TABLE_NUMBER_FORMAT,
    VIDEO_TABLE_PREFIX_SPACING,
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
import re
import time


def _fmt_table_no(value: str, fmt: str) -> str:
    if fmt == "as-is":
        return value
    m = re.search(r"\d+", value)
    digits = m.group() if m else value
    return digits.zfill(2) if fmt == "padded" else digits


class DigitalVideoBannerGenerator:
    def __init__(self, output_path=None):
        self.input_path = VIDEO_INPUT_PATH
        self.output_path = output_path or VIDEO_OUTPUT_PATH
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

    def _fit_font_size(self, name: str) -> int:
        font_size = VIDEO_NAME_FONT_SIZE
        while font_size > VIDEO_NAME_FONT_SIZE_MIN:
            font = ImageFont.truetype(self.font, font_size)
            bbox = font.getbbox(name)
            if (bbox[2] - bbox[0]) <= VIDEO_NAME_MAX_WIDTH:
                break
            font_size -= VIDEO_NAME_FONT_SIZE_STEP
        return font_size

    def generate_name(self, name):
        casing = VIDEO_NAME_CASING
        if casing == "upper":
            name = name.upper()
        elif casing == "lower":
            name = name.lower()
        elif casing == "as-is":
            pass
        else:
            name = name.title()
        font_size = self._fit_font_size(name)
        name_text = TextClip(
            text=name,
            font_size=font_size,
            color=self.font_color,
            font=self.font,
            duration=self.text_duration,
        )
        name_text = name_text.with_position((self.name_pos_x, self.name_pos_y))
        name_text = name_text.with_effects([CrossFadeIn(self.text_fade_duration)])
        name_text = name_text.with_start(self.text_entrance_time)
        return name_text

    def generate_table_num(self, no):
        formatted_table_num = "{}{}{}".format(VIDEO_TABLE_PREFIX, " " * VIDEO_TABLE_PREFIX_SPACING, _fmt_table_no(no, VIDEO_TABLE_NUMBER_FORMAT))
        table_no = TextClip(
            text=formatted_table_num,
            font_size=self.table_num_font_size,
            color=self.font_color,
            font=self.font,
            duration=self.text_duration,
        )
        table_no = table_no.with_position((self.table_num_pos_x, self.table_num_pos_y))
        table_no = table_no.with_effects([CrossFadeIn(self.text_fade_duration)])
        table_no = table_no.with_start(self.text_entrance_time)
        return table_no

    def output_video(self, final_video, output_name, branch):
        output_path = os.path.join(self.output_path, branch)
        os.makedirs(output_path, exist_ok=True)
        output = os.path.join(output_path, output_name)
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
        gen_name = self.generate_name(name)
        table = self.generate_table_num(table_num)
        final_video = CompositeVideoClip(
            [input_video, gen_name, table], use_bgclip=True
        )
        final_video = final_video.with_audio(input_video_audio)
        output_name = self.generate_output_video_name(name, table_num)
        self.output_video(final_video, output_name, branch)
        input_video.close()

    @time_decorator
    def process_videos(self, digital_cards: list[DigitalCard], progress_tracker=None):
        for card in digital_cards:
            while progress_tracker and progress_tracker.is_paused():
                time.sleep(1)

            id = card.get_id()
            name = card.get_name()
            table_no = card.get_table_number()
            language = card.get_language()
            branch = card.get_branch()

            start = time.time()
            self.process_video(name, table_no, language, branch, id)
            elapsed = time.time() - start

            if progress_tracker:
                progress_tracker.update(id, name, elapsed)


if __name__ == "__main__":
    generator = DigitalVideoBannerGenerator()
    generator.process_video("Albert Einstein", "T3")

    # TODO: check for duplicated data (Validation)
    # Divide the task to use multiple threads for processing to improve processing speed.
    # Compression of the output with lossless compression
