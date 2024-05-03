from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# Load your video
video = VideoFileClip("/Users/junkangwong/Documents/github_repo/digital_card/input/sample_vid.mp4")

# Create a text clip. The text clip has transparent background by default.
text = TextClip("Hello, World!", fontsize=70, color='black', font='Amiri-Bold', size=video.size)

# Set duration for the text and its position
text = text.set_duration(4).set_position("center")

# Apply fade-in and fade-out effects (fading from transparent to white and then to black)
text = text.crossfadein(1)

# Set the text to appear at a specific time
text = text.set_start(4)

# Composite the text onto the video
final_video = CompositeVideoClip([video, text], use_bgclip=True)

# Write the result to a file
final_video.write_videofile("/Users/junkangwong/Documents/github_repo/digital_card/output/output_video.mp4", codec='libx264', bitrate="5000k")