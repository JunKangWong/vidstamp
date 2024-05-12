from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip


class DigitalVideoBannerGenerator:
    def __init__(self):
        # Configurations
        self.input_path = "/Users/junkangwong/Documents/github_repo/digital_card/input/sample_vid5.mp4"
        self.output_path = "/Users/junkangwong/Documents/github_repo/digital_card/output/output_sample_sound2.mp4"
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

    def load_video(self, input_path):
        self.input_video = VideoFileClip(input_path)
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

    def output_video(self, final_video):
        final_video.write_videofile(
            self.output_path,
            codec=self.codec,
            audio_codec=self.audio_codec,  # Specify AAC audio codec
            bitrate=self.bit_rate,
        )

    def process_all(self):
        self.load_video(self.input_path)
        final_video = self.compose_video("Baby Johnson", "T2")
        self.output_video(final_video)


if __name__ == "__main__":
    generator = DigitalVideoBannerGenerator()
    generator.process_all()

    # Read from excel
    # TODO: check for duplicated data from excel (Validation)
    # Length check (optional)
    # Divide the task to use multiple threads for processing to improve processing speed.
    # Compression of the output with lossless compression
