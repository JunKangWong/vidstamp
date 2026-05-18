import os
from pathlib import Path

_HERE = Path(__file__).parent

# ─── Paths ────────────────────────────────────────────────────────────────────

# Input CSV for image card generation
IMAGE_CSV_PATH = str(_HERE / "input" / "sample_namelist.csv")

# Input CSV for video banner generation
VIDEO_CSV_PATH = str(_HERE / "input" / "trr_invitation_batch_1.csv")

# Image template drawn on for each card
IMAGE_TEMPLATE_PATH = str(_HERE / "template" / "trr_invitation.png")

# Font file used for both image cards and video overlays (path relative to project root)
FONT_FILENAME = "font/biondi/biondi-sans-rg-AF65ded4d89bfb4.otf"
FONT_PATH = str(_HERE / FONT_FILENAME)

# Output ZIP that bundles all generated image cards
IMAGE_OUTPUT_ZIP_PATH = "/Users/junkang/Documents/repo/personal/digital_card_generator/output/digital_cards.zip"

# Directory where source MP4 video files are located
VIDEO_INPUT_PATH = str(_HERE / "template")

# Root output directory for generated video banners (one subfolder per branch)
VIDEO_OUTPUT_PATH = "/Users/junkang/Documents/repo/personal/digital_card_generator/output/digital_video_banner"

# Directory for log files and resume state
LOG_DIR = str(_HERE / "output" / "log")

# Derived log file paths — change LOG_DIR above to relocate both
LOG_FILE_PATH = os.path.join(LOG_DIR, "digital_video_banner.log")
LAST_PROCESSED_ID_PATH = os.path.join(LOG_DIR, "last_processed_id.txt")

# Pause sentinel file — create this file to pause generation before the next video
PAUSE_FILE_PATH = os.path.join(LOG_DIR, "PAUSE")

# JSON file updated after each video with progress info (total, done, percentage, ETA)
PROGRESS_FILE_PATH = os.path.join(LOG_DIR, "progress.json")

# Source video filenames — must exist inside VIDEO_INPUT_PATH
# Set both to the same file if there is no language distinction
VIDEO_EN_FILENAME = "INVITATIONC FINAL ADD NAME.mp4"  # Used when language == "E"
VIDEO_CN_FILENAME = "INVITATIONC FINAL ADD NAME.mp4"  # Used when language == "C" or blank

# ─── Image Card Settings ──────────────────────────────────────────────────────

# Font size for the attendee name drawn on image cards
IMAGE_NAME_FONT_SIZE = 145

# Font size for the table number drawn on image cards
IMAGE_TABLE_FONT_SIZE = 70

# Y-coordinate (pixels from top) where the attendee name is placed on the card
IMAGE_NAME_Y = 1125

# Y-coordinate (pixels from top) where the table number is placed on the card
IMAGE_TABLE_Y = 1300

# ─── Video Banner — Encoding ──────────────────────────────────────────────────

# Video encoding codec (e.g. "libx264", "libx265")
VIDEO_CODEC = "libx264"

# Audio encoding codec
VIDEO_AUDIO_CODEC = "aac"

# Output video bitrate — higher = better quality, larger file size
VIDEO_BITRATE = "5000k"

# ─── Video Banner — Text & Font ───────────────────────────────────────────────

# Default font size for the attendee name overlay
VIDEO_NAME_FONT_SIZE = 48

# Font size used when name length exceeds VIDEO_NAME_LENGTH_MEDIUM_THRESHOLD
VIDEO_NAME_FONT_SIZE_MEDIUM = 45

# Font size used when name length exceeds VIDEO_NAME_LENGTH_LONG_THRESHOLD
VIDEO_NAME_FONT_SIZE_SMALL = 30

# Character count above which medium font size kicks in
VIDEO_NAME_LENGTH_MEDIUM_THRESHOLD = 25

# Character count above which small font size kicks in
VIDEO_NAME_LENGTH_LONG_THRESHOLD = 35

# Font size for the table number overlay
VIDEO_TABLE_FONT_SIZE = 26

# Text color for all overlays (name + table number)
VIDEO_FONT_COLOR = "white"

# ─── Video Banner — Text Positioning ─────────────────────────────────────────

# Horizontal position of the name overlay ("center" or pixel offset from left)
VIDEO_NAME_POS_X = "center"

# Vertical position of the name overlay (negative = offset up from bottom)
VIDEO_NAME_POS_Y = 620

# Horizontal position of the table number overlay
VIDEO_TABLE_POS_X = "center"

# Vertical position of the table number overlay (negative = offset up from bottom)
VIDEO_TABLE_POS_Y = 690

# ─── Video Banner — Text Timing ───────────────────────────────────────────────

# How long (seconds) the text overlays remain visible (video is 18.34s)
VIDEO_TEXT_DURATION = 15.0

# Duration (seconds) of the crossfade-in effect when text overlays appear
VIDEO_TEXT_FADE_DURATION = 1

# Delay (seconds) before text overlays appear after the video starts
VIDEO_TEXT_ENTRANCE_TIME = 5.0
