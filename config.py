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

# Pixel format — yuv420p is universally compatible (Windows, VLC, phones)
# yuv444p preserves more colour but many Windows decoders reject it
VIDEO_PIXEL_FORMAT = "yuv420p"

# Output video bitrate — higher = better quality, larger file size
VIDEO_BITRATE = "5000k"

# ─── Video Banner — Text & Font ───────────────────────────────────────────────

# Default (maximum) font size for the attendee name overlay
VIDEO_NAME_FONT_SIZE = 48

# Minimum font size — name is rendered at this size if it still overflows
VIDEO_NAME_FONT_SIZE_MIN = 24

# Points to reduce font size by on each fitting iteration
VIDEO_NAME_FONT_SIZE_STEP = 2

# Maximum pixel width for the rendered name; names wider than this are shrunk
# until they fit (or until VIDEO_NAME_FONT_SIZE_MIN is reached).
# Frame width is 1080px; 900px leaves ~90px margin on each side.
VIDEO_NAME_MAX_WIDTH = 900

# Pixels of breathing room subtracted from each side of the max-width zone.
# Effective name constraint = VIDEO_NAME_MAX_WIDTH - 2 * VIDEO_NAME_MARGIN
VIDEO_NAME_MARGIN = 0

# Font size for the table number overlay
VIDEO_TABLE_FONT_SIZE = 26

# Prefix prepended to the table number value (e.g. "Table No: " → "Table No: K8")
# Set to "" to render just the raw table number
VIDEO_TABLE_PREFIX = "Table Number:"

# How to format the table number value from the CSV
# "as-is"  → show exactly as stored (e.g. "K8", "T1")
# "number" → strip leading letters, show digits only (e.g. "8", "1")
# "padded" → strip leading letters, zero-pad to 2 digits (e.g. "08", "01")
VIDEO_TABLE_NUMBER_FORMAT = "as-is"

# Number of spaces inserted between the prefix and the table number
VIDEO_TABLE_PREFIX_SPACING = 1

# Casing applied to the full table text (prefix + number) before rendering
# Options: "title" (Title Case), "upper" (ALL CAPS), "lower" (all lowercase), "as-is" (no change)
VIDEO_TABLE_CASING = "upper"

# Casing applied to the attendee name before rendering
# Options: "title" (Title Case), "upper" (ALL CAPS), "lower" (all lowercase), "as-is" (no change)
VIDEO_NAME_CASING = "upper"

# Text color for all overlays (name + table number)
VIDEO_FONT_COLOR = "white"

# ─── Video Banner — Text Positioning ─────────────────────────────────────────

# Horizontal position of the name overlay ("center" or pixel offset from left)
VIDEO_NAME_POS_X = "center"

# Vertical position of the name overlay (negative = offset up from bottom)
VIDEO_NAME_POS_Y = 630

# Horizontal position of the table number overlay
VIDEO_TABLE_POS_X = "center"

# Vertical position of the table number overlay (negative = offset up from bottom)
VIDEO_TABLE_POS_Y = 685

# ─── Video Banner — Text Timing ───────────────────────────────────────────────

# How long (seconds) the text overlays remain visible (video is 18.34s)
VIDEO_TEXT_DURATION = 15.0

# Duration (seconds) of the crossfade-in effect when text overlays appear
VIDEO_TEXT_FADE_DURATION = 1

# Delay (seconds) before text overlays appear after the video starts
VIDEO_TEXT_ENTRANCE_TIME = 4.5
