from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from digital_card_generator import DigitalCard
from utility import time_decorator
import datetime


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

        # Instance variable
        self.input_video = None
        self.input_video_audio = None
        self.input_video_size = None
        self.name = "Patricia Thomas"  # TODO: accept a list of name and table number, maybe do not have to reload video repeatedly...

        # Load video into memory
        self.load_video()

    def load_video(self):
        self.input_video = VideoFileClip(self.input_path)
        self.input_video_audio = self.input_video.audio
        self.input_video_size = self.input_video.size

    def generate_name(self, name):
        name_text = TextClip(
            name,
            fontsize=self.name_font_size,
            color=self.font_color,
            font=self.font,
            size=self.input_video_size,
        )
        name_text = name_text.set_duration(self.text_duration).set_position(
            (self.name_pos_x, self.name_pos_y)
        )
        name_text = name_text.crossfadein(self.text_fade_duration)
        name_text = name_text.set_start(self.text_entrance_time)
        return name_text

    # TODO: remove one of these, they are the same, parameterize the table_num_pos except the text and some sizes.
    def generate_table_num(self, no):
        formatted_table_num = "Table No: {}".format(no)
        table_no = TextClip(
            formatted_table_num,
            fontsize=self.table_num_font_size,
            color=self.font_color,
            font=self.font,
            size=self.input_video_size,
        )
        table_no = table_no.set_duration(self.text_duration).set_position(
            (self.table_num_pos_x, self.table_num_pos_y)
        )
        table_no = table_no.crossfadein(self.text_fade_duration)
        table_no = table_no.set_start(self.text_entrance_time)
        return table_no

    def compose_video(self, name, table_num):
        name = self.generate_name(name)
        table = self.generate_table_num(table_num)
        final_video = CompositeVideoClip(
            [self.input_video, name, table], use_bgclip=True
        )
        final_video = final_video.set_audio(self.input_video_audio)
        return final_video

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

    @time_decorator
    def process_video(self, name, table_num):
        final_video = self.compose_video(name, table_num)
        output_name = self.generate_output_video_name(name, table_num)
        self.output_video(final_video, output_name)

    @time_decorator
    def process_videos(self, digital_cards: list[DigitalCard]):
        for card in digital_cards:
            name = card.get_name()
            table_no = card.get_table_number()
            self.process_video(name, table_no)


if __name__ == "__main__":
    generator = DigitalVideoBannerGenerator()
    generator.process_video("Albert Einstein", "T3")

    # Read from excel
    # TODO: check for duplicated data from excel (Validation)
    # Length check (optional)
    # Divide the task to use multiple threads for processing to improve processing speed.
    # Compression of the output with lossless compression
