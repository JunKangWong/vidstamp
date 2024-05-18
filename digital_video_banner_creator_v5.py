from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from digital_card_generator import DigitalCard
from utility import time_decorator, log_execution_time_with_details
import os


class DigitalVideoBannerGenerator:
    def __init__(self):
        # Configurations
        self.input_path = "/Users/junkangwong/Documents/github_repo/digital_card/input"
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

    def generate_name(self, name, vid_size):
        size = len(name)
        font_size = self.name_font_size
        if size > 35:
            font_size = 30
        elif size > 25:
            font_size = 45
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

    def compose_video(self, name, table_num):
        name = self.generate_name(name)
        table = self.generate_table_num(table_num)
        final_video = CompositeVideoClip(
            [self.input_video, name, table], use_bgclip=True
        )
        final_video = final_video.set_audio(self.input_video_audio)
        return final_video

    def output_video(self, final_video, output_name, branch):
        output_path = os.path.join(self.output_path, branch)  # Use os.path.join
        os.makedirs(output_path, exist_ok=True)
        output = "{}/{}".format(output_path, output_name)
        final_video.write_videofile(
            output,
            codec=self.codec,
            audio_codec=self.audio_codec,  # Specify AAC audio codec
            bitrate=self.bit_rate,
        )

    def generate_output_video_name(self, name, table_num):
        name = name.title()
        name = name.replace("\\", "")
        name = name.replace("/", "")
        return "T{}_{}.mp4".format(table_num, name)

    @log_execution_time_with_details
    def process_video(self, name, table_num, language, branch, id=None):
        if language == "E":
            filename = "TRR_E_Invitation_EN_S.mp4"
        else:
            filename = "TRR_E_Invitation_CN_S.mp4"
        input_path = os.path.join(self.input_path, filename)  # Use os.path.join
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
