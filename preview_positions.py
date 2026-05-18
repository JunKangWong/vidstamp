"""
Preview script for tuning text positions without rendering a full video.

Extracts one frame from the template video, draws the name + table number
overlays using the same config values as the real video renderer, then opens
the result. Tune positions in config.py, re-run this — no video encoding.

Usage:
    python3 preview_positions.py                         # first CSV row, default frame
    python3 preview_positions.py "Hoi Pheh Leng" K8     # custom name, default frame
    python3 preview_positions.py --at 10                 # first CSV row, t=10s
    python3 preview_positions.py "Hoi Pheh Leng" K8 --at 10.5
"""

import argparse
import os
import csv
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip
from config import (
    VIDEO_INPUT_PATH,
    VIDEO_CSV_PATH,
    VIDEO_EN_FILENAME,
    VIDEO_CN_FILENAME,
    FONT_PATH,
    VIDEO_NAME_FONT_SIZE,
    VIDEO_NAME_FONT_SIZE_MEDIUM,
    VIDEO_NAME_FONT_SIZE_SMALL,
    VIDEO_NAME_LENGTH_MEDIUM_THRESHOLD,
    VIDEO_NAME_LENGTH_LONG_THRESHOLD,
    VIDEO_TABLE_FONT_SIZE,
    VIDEO_FONT_COLOR,
    VIDEO_NAME_POS_X,
    VIDEO_NAME_POS_Y,
    VIDEO_TABLE_POS_X,
    VIDEO_TABLE_POS_Y,
    VIDEO_TEXT_ENTRANCE_TIME,
    VIDEO_TEXT_FADE_DURATION,
)

PREVIEW_OUTPUT = "./output/preview.png"
ANCHOR_MARK_COLOR = "red"
ANCHOR_MARK_SIZE = 12


def pick_name_font_size(name: str) -> int:
    """Mirror the adaptive sizing in video_renderer.generate_name."""
    if len(name) > VIDEO_NAME_LENGTH_LONG_THRESHOLD:
        return VIDEO_NAME_FONT_SIZE_SMALL
    if len(name) > VIDEO_NAME_LENGTH_MEDIUM_THRESHOLD:
        return VIDEO_NAME_FONT_SIZE_MEDIUM
    return VIDEO_NAME_FONT_SIZE


def resolve_position(pos_x, pos_y, text_w: int, frame_w: int, frame_h: int):
    """Convert moviepy-style positions to absolute PIL top-left pixel coords."""
    if pos_x == "center":
        x = (frame_w - text_w) // 2
    else:
        x = int(pos_x) if int(pos_x) >= 0 else frame_w + int(pos_x)

    # Negative Y = offset from bottom (moviepy convention)
    y = int(pos_y) if int(pos_y) >= 0 else frame_h + int(pos_y)
    return x, y


def draw_anchor_crosshair(draw: ImageDraw.ImageDraw, x: int, y: int):
    """Tiny red + mark at the text anchor so the exact pixel is visible."""
    s = ANCHOR_MARK_SIZE
    draw.line((x - s, y, x + s, y), fill=ANCHOR_MARK_COLOR, width=2)
    draw.line((x, y - s, x, y + s), fill=ANCHOR_MARK_COLOR, width=2)


def load_default_sample():
    """Pull first row from the configured CSV as the sample text."""
    try:
        with open(VIDEO_CSV_PATH, newline="") as f:
            row = next(csv.DictReader(f))
            return row["name"], row["table_no"]
    except (FileNotFoundError, StopIteration, KeyError):
        return "Sample Name", "T1"


def main():
    parser = argparse.ArgumentParser(description="Preview text positions on a video frame.")
    parser.add_argument("name", nargs="?", default=None, help="Attendee name")
    parser.add_argument("table_num", nargs="?", default=None, help="Table number")
    parser.add_argument("--at", type=float, default=None, metavar="SECONDS",
                        help="Which second of the video to use as the preview frame "
                             "(default: VIDEO_TEXT_ENTRANCE_TIME + VIDEO_TEXT_FADE_DURATION)")
    args = parser.parse_args()

    if args.name and args.table_num:
        name, table_num = args.name, args.table_num
    else:
        name, table_num = load_default_sample()

    video_path = os.path.join(VIDEO_INPUT_PATH, VIDEO_CN_FILENAME)
    if not os.path.exists(video_path):
        video_path = os.path.join(VIDEO_INPUT_PATH, VIDEO_EN_FILENAME)

    clip = VideoFileClip(video_path)
    frame_time = args.at if args.at is not None else VIDEO_TEXT_ENTRANCE_TIME + VIDEO_TEXT_FADE_DURATION
    frame_time = min(frame_time, clip.duration - 0.1)
    frame = clip.get_frame(frame_time)
    clip.close()

    img = Image.fromarray(frame)
    frame_w, frame_h = img.size
    draw = ImageDraw.Draw(img)

    # Name overlay
    name_text = name.title()
    name_font = ImageFont.truetype(FONT_PATH, pick_name_font_size(name_text))
    nx0, ny0, nx1, ny1 = draw.textbbox((0, 0), name_text, font=name_font)
    name_w = nx1 - nx0
    name_x, name_y = resolve_position(
        VIDEO_NAME_POS_X, VIDEO_NAME_POS_Y, name_w, frame_w, frame_h
    )
    draw.text((name_x, name_y), name_text, fill=VIDEO_FONT_COLOR, font=name_font)
    draw_anchor_crosshair(draw, name_x, name_y)

    # Table number overlay
    table_text = f"Table No: {table_num}"
    table_font = ImageFont.truetype(FONT_PATH, VIDEO_TABLE_FONT_SIZE)
    tx0, ty0, tx1, ty1 = draw.textbbox((0, 0), table_text, font=table_font)
    table_w = tx1 - tx0
    table_x, table_y = resolve_position(
        VIDEO_TABLE_POS_X, VIDEO_TABLE_POS_Y, table_w, frame_w, frame_h
    )
    draw.text((table_x, table_y), table_text, fill=VIDEO_FONT_COLOR, font=table_font)
    draw_anchor_crosshair(draw, table_x, table_y)

    os.makedirs(os.path.dirname(PREVIEW_OUTPUT), exist_ok=True)
    img.save(PREVIEW_OUTPUT)
    print(
        f"Preview saved: {PREVIEW_OUTPUT}\n"
        f"  Frame: {frame_w}x{frame_h} @ t={frame_time:.2f}s\n"
        f"  Name  '{name_text}' -> ({name_x}, {name_y}), size {name_font.size}\n"
        f"  Table '{table_text}' -> ({table_x}, {table_y}), size {table_font.size}"
    )
    img.show()


if __name__ == "__main__":
    main()
