from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# Load your video
video = VideoFileClip("/Users/junkangwong/Documents/github_repo/digital_card/input/sample_vid5.mp4")

# TODO:  Make all dynamic values parameterized with same variable
# Attendees name
# Create a text clip. The text clip has transparent background by default.
text = TextClip("Patricia Thomas", fontsize=54, color='black', font='./font/BASKVILL.ttf', size=video.size)

# Set duration for the text and its position
text = text.set_duration(9.5).set_position(("center", -230))

# Apply fade-in and fade-out effects (fading from transparent to white and then to black)
text = text.crossfadein(1)

# Set the text to appear at a specific time
text = text.set_start(0.5)

# Table Number
# Create a text clip. The text clip has transparent background by default.
table_no = TextClip("Table No: T1", fontsize=28, color='black', font='./font/BASKVILL.ttf', size=video.size)

# Set duration for the text and its position
table_no = table_no.set_duration(9.5).set_position(("center", -176))

# Apply fade-in and fade-out effects (fading from transparent to white and then to black)
table_no = table_no.crossfadein(1)

# Set the text to appear at a specific time
table_no = table_no.set_start(0.5) 


# Composite the text onto the video
final_video = CompositeVideoClip([video, text, table_no], use_bgclip=True)

# Add back the audio
final_video = final_video.set_audio(video.audio )


# Write the result to a file
final_video.write_videofile("/Users/junkangwong/Documents/github_repo/digital_card/output/output_sample_sound2.mp4",
                            codec='libx264', 
                            audio_codec='aac',  # Specify AAC audio codec
                            bitrate="5000k")