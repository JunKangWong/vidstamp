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

from __future__ import annotations

import argparse
import os
import csv
import re
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip
from config import (
    VIDEO_INPUT_PATH,
    VIDEO_CSV_PATH,
    VIDEO_EN_FILENAME,
    VIDEO_CN_FILENAME,
    FONT_PATH,
    VIDEO_NAME_FONT_SIZE,
    VIDEO_NAME_FONT_SIZE_MIN,
    VIDEO_NAME_FONT_SIZE_STEP,
    VIDEO_NAME_MAX_WIDTH,
    VIDEO_NAME_MARGIN,
    VIDEO_NAME_CASING,
    VIDEO_TABLE_FONT_SIZE,
    VIDEO_TABLE_PREFIX,
    VIDEO_TABLE_NUMBER_FORMAT,
    VIDEO_TABLE_PREFIX_SPACING,
    VIDEO_TABLE_CASING,
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


def _fmt_table_no(value: str, fmt: str) -> str:
    if fmt == "as-is":
        return value
    m = re.search(r"\d+", value)
    digits = m.group() if m else value
    return digits.zfill(2) if fmt == "padded" else digits


def fit_name_font_size(name: str, font_path: str, max_size: int, min_size: int,
                       step: int, max_width: int) -> int:
    """Mirror the pixel-width fitting in video_renderer._fit_font_size."""
    font_size = max_size
    while font_size > min_size:
        font = ImageFont.truetype(font_path, font_size)
        bbox = font.getbbox(name)
        if (bbox[2] - bbox[0]) <= max_width:
            break
        font_size -= step
    return font_size


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


def _load_base_frame(at_time: float | None = None):
    """Load the template video and extract a single frame as a PIL Image."""
    video_path = os.path.join(VIDEO_INPUT_PATH, VIDEO_CN_FILENAME)
    if not os.path.exists(video_path):
        video_path = os.path.join(VIDEO_INPUT_PATH, VIDEO_EN_FILENAME)

    clip = VideoFileClip(video_path)
    frame_time = at_time if at_time is not None else VIDEO_TEXT_ENTRANCE_TIME + VIDEO_TEXT_FADE_DURATION
    frame_time = min(frame_time, clip.duration - 0.1)
    frame = clip.get_frame(frame_time)
    clip.close()
    return Image.fromarray(frame), frame_time


def generate_preview_image(
    name: str,
    table_no: str,
    overrides: dict | None = None,
    base_frame: "Image.Image | None" = None,
    at_time: float | None = None,
    draw_anchors: bool = True,
) -> Image.Image:
    """
    Render a single preview frame with name + table overlays.

    Args:
        name: Attendee name (rendered title-cased).
        table_no: Table number string (rendered as "Table No: {value}").
        overrides: Optional dict of config var names → values. Shadows the
            imported config constants for this call only. Nothing is written
            to disk. Useful for the web UI to do live previews without
            mutating config.py.
        base_frame: Pre-extracted PIL Image to draw on. When provided, the
            video file is NOT loaded — this is the fast path used by the
            web server (cached frame). When None, the video is opened and a
            frame is extracted (CLI path).
        at_time: If base_frame is None, which second of the video to grab.
        draw_anchors: Whether to overlay red crosshairs at the text anchors.

    Returns:
        A new PIL Image with overlays drawn. The original base_frame is not
        mutated when callers pass a copy.
    """
    def _r(key, default):
        return overrides.get(key, default) if overrides else default

    name_pos_x = _r("VIDEO_NAME_POS_X", VIDEO_NAME_POS_X)
    name_pos_y = _r("VIDEO_NAME_POS_Y", VIDEO_NAME_POS_Y)
    table_pos_x = _r("VIDEO_TABLE_POS_X", VIDEO_TABLE_POS_X)
    table_pos_y = _r("VIDEO_TABLE_POS_Y", VIDEO_TABLE_POS_Y)
    name_size_max = _r("VIDEO_NAME_FONT_SIZE", VIDEO_NAME_FONT_SIZE)
    name_size_min = _r("VIDEO_NAME_FONT_SIZE_MIN", VIDEO_NAME_FONT_SIZE_MIN)
    name_size_step = _r("VIDEO_NAME_FONT_SIZE_STEP", VIDEO_NAME_FONT_SIZE_STEP)
    name_max_width = _r("VIDEO_NAME_MAX_WIDTH", VIDEO_NAME_MAX_WIDTH)
    name_margin = _r("VIDEO_NAME_MARGIN", VIDEO_NAME_MARGIN)
    name_casing = _r("VIDEO_NAME_CASING", VIDEO_NAME_CASING)
    table_prefix = _r("VIDEO_TABLE_PREFIX", VIDEO_TABLE_PREFIX)
    table_number_fmt = _r("VIDEO_TABLE_NUMBER_FORMAT", VIDEO_TABLE_NUMBER_FORMAT)
    table_prefix_spacing = _r("VIDEO_TABLE_PREFIX_SPACING", VIDEO_TABLE_PREFIX_SPACING)
    table_casing = _r("VIDEO_TABLE_CASING", VIDEO_TABLE_CASING)
    table_font_size = _r("VIDEO_TABLE_FONT_SIZE", VIDEO_TABLE_FONT_SIZE)
    font_color = _r("VIDEO_FONT_COLOR", VIDEO_FONT_COLOR)
    font_path = _r("FONT_PATH", FONT_PATH)

    if base_frame is None:
        img, _ = _load_base_frame(at_time)
    else:
        img = base_frame

    frame_w, frame_h = img.size

    effective_width = name_max_width - 2 * name_margin

    if draw_anchors:
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        cx = frame_w // 2
        for x in (cx - name_max_width // 2, cx + name_max_width // 2):
            od.line([(x, 0), (x, frame_h)], fill=(0, 220, 255, 160), width=2)
        if name_margin > 0:
            for x in (cx - effective_width // 2, cx + effective_width // 2):
                od.line([(x, 0), (x, frame_h)], fill=(255, 230, 0, 160), width=2)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(img)

    if name_casing == "upper":
        name_text = name.upper()
    elif name_casing == "lower":
        name_text = name.lower()
    elif name_casing == "as-is":
        name_text = name
    else:
        name_text = name.title()
    name_font_size = fit_name_font_size(
        name_text, font_path, name_size_max, name_size_min, name_size_step, effective_width,
    )
    name_font = ImageFont.truetype(font_path, name_font_size)
    nx0, ny0, nx1, ny1 = draw.textbbox((0, 0), name_text, font=name_font)
    name_w = nx1 - nx0
    name_x, name_y = resolve_position(name_pos_x, name_pos_y, name_w, frame_w, frame_h)
    draw.text((name_x, name_y), name_text, fill=font_color, font=name_font)
    if draw_anchors:
        draw_anchor_crosshair(draw, name_x, name_y)

    table_text = f"{table_prefix}{' ' * table_prefix_spacing}{_fmt_table_no(table_no, table_number_fmt)}"
    if table_casing == "upper":
        table_text = table_text.upper()
    elif table_casing == "lower":
        table_text = table_text.lower()
    elif table_casing == "title":
        table_text = table_text.title()
    table_font = ImageFont.truetype(font_path, table_font_size)
    tx0, ty0, tx1, ty1 = draw.textbbox((0, 0), table_text, font=table_font)
    table_w = tx1 - tx0
    table_x, table_y = resolve_position(table_pos_x, table_pos_y, table_w, frame_w, frame_h)
    draw.text((table_x, table_y), table_text, fill=font_color, font=table_font)
    if draw_anchors:
        draw_anchor_crosshair(draw, table_x, table_y)

    return img


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

    base_frame, frame_time = _load_base_frame(args.at)
    img = generate_preview_image(name, table_num, base_frame=base_frame)

    os.makedirs(os.path.dirname(PREVIEW_OUTPUT), exist_ok=True)
    img.save(PREVIEW_OUTPUT)
    frame_w, frame_h = img.size
    print(
        f"Preview saved: {PREVIEW_OUTPUT}\n"
        f"  Frame: {frame_w}x{frame_h} @ t={frame_time:.2f}s"
    )
    img.show()


if __name__ == "__main__":
    main()
