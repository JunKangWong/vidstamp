from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# Create a text clip
text = TextClip("Hello, World!", fontsize=70, color='white', font='Amiri-Bold')
text = text.set_duration(4).set_pos('center').fadein(1)

# Load the video
video = VideoFileClip("/Users/junkangwong/Documents/github_repo/digital_card/input/sample_vid.mp4")

# Overlay the text on the video starting from the 4th second
final_video = CompositeVideoClip([video, text.set_start(4)])

# Write the result to a file
final_video.write_videofile("/Users/junkangwong/Documents/github_repo/digital_card/output/output_video.mp4", codec='libx264', bitrate="5000k")