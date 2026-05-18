"""
Live-preview configuration UI for the digital card generator.

Run:
    python app.py
    # open http://localhost:5000

The server caches the template video's preview frame at startup so each live
preview request is just a PIL draw on a copy of the cached frame — fast enough
to update on every slider movement.

Save flow: backs up the current config.py to ./output/config_backup/ with a
datetime stamp, then rewrites only the targeted config lines via regex so all
comments and formatting are preserved.
"""

from __future__ import annotations

import io
import os
import re
import subprocess
import sys
import threading
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from moviepy import VideoFileClip
from PIL import Image

import config
from preview_positions import generate_preview_image
from progress_tracker import ProgressTracker

# Fields exposed in the UI (everything else in config.py stays manually edited).
UI_KEYS = [
    "VIDEO_NAME_POS_X", "VIDEO_NAME_POS_Y",
    "VIDEO_TABLE_POS_X", "VIDEO_TABLE_POS_Y",
    "VIDEO_NAME_FONT_SIZE", "VIDEO_NAME_FONT_SIZE_MIN", "VIDEO_NAME_FONT_SIZE_STEP",
    "VIDEO_NAME_MAX_WIDTH", "VIDEO_NAME_CASING",
    "VIDEO_TABLE_PREFIX", "VIDEO_TABLE_NUMBER_FORMAT", "VIDEO_TABLE_PREFIX_SPACING",
    "VIDEO_TABLE_FONT_SIZE", "VIDEO_FONT_COLOR",
    "VIDEO_TEXT_ENTRANCE_TIME",
    "FONT_FILENAME",
    "VIDEO_OUTPUT_PATH",
    "IMAGE_NAME_Y", "IMAGE_TABLE_Y",
    "IMAGE_NAME_FONT_SIZE", "IMAGE_TABLE_FONT_SIZE",
    "IMAGE_OUTPUT_ZIP_PATH",
]

CONFIG_FILE = Path(__file__).parent / "config.py"
BACKUP_DIR = Path(__file__).parent / "output" / "config_backup"
FONT_DIR = Path(__file__).parent / "font"

# Keep the clip alive so we can re-extract frames on demand without re-opening
# the 31 MB file each time. Cache extracted frames by timestamp.
VIDEO_CLIP: VideoFileClip | None = None
VIDEO_DURATION: float = 0.0
FRAME_CACHE: dict[float, Image.Image] = {}
FRAME_CACHE_MAX = 20

app = Flask(__name__)

# job_id -> {"status": "running"|"done"|"error", "lines": [...]}
_jobs: dict[str, dict] = {}


def open_clip() -> tuple[VideoFileClip, float]:
    """Open the template video and return the clip + its duration."""
    video_path = os.path.join(config.VIDEO_INPUT_PATH, config.VIDEO_CN_FILENAME)
    if not os.path.exists(video_path):
        video_path = os.path.join(config.VIDEO_INPUT_PATH, config.VIDEO_EN_FILENAME)
    clip = VideoFileClip(video_path)
    return clip, clip.duration


def get_frame_at(t: float) -> Image.Image:
    """Return a PIL Image for the requested second, caching extracted frames."""
    assert VIDEO_CLIP is not None
    t = max(0.0, min(t, VIDEO_DURATION - 0.1))
    key = round(t, 2)
    if key not in FRAME_CACHE:
        if len(FRAME_CACHE) >= FRAME_CACHE_MAX:
            FRAME_CACHE.pop(next(iter(FRAME_CACHE)))
        FRAME_CACHE[key] = Image.fromarray(VIDEO_CLIP.get_frame(key))
    return FRAME_CACHE[key]


def default_frame_time() -> float:
    return min(config.VIDEO_TEXT_ENTRANCE_TIME, VIDEO_DURATION - 0.1)


def current_config_values() -> dict:
    """Snapshot the UI-exposed config vars from the imported module."""
    return {key: getattr(config, key) for key in UI_KEYS}


def format_value_for_config(value) -> str:
    """Render a Python value back into source form for config.py."""
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, (int, float)):
        return repr(value)
    return f'"{value}"'


def rewrite_config(updates: dict) -> str:
    """
    Backup current config.py, then rewrite each updated line in place.
    Returns the relative backup path.
    """
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_path = BACKUP_DIR / f"config_{timestamp}.py"

    original_text = CONFIG_FILE.read_text()
    backup_path.write_text(original_text)

    new_text = original_text
    for key, value in updates.items():
        if key not in UI_KEYS:
            continue
        new_value = format_value_for_config(value)
        pattern = re.compile(
            rf"^({re.escape(key)}\s*=\s*)(.+?)(\s*(?:#.*)?)$",
            re.MULTILINE,
        )
        new_text, count = pattern.subn(
            lambda m: f"{m.group(1)}{new_value}{m.group(3)}",
            new_text,
            count=1,
        )
        if count == 0:
            raise ValueError(f"Could not find assignment for {key} in config.py")

    CONFIG_FILE.write_text(new_text)

    # Refresh the in-memory config so /config GETs reflect the new state.
    for key, value in updates.items():
        if key in UI_KEYS:
            setattr(config, key, value)

    return str(backup_path.relative_to(Path(__file__).parent))


def coerce_value(key: str, value):
    """Coerce JSON values to the right Python type based on current config."""
    current = getattr(config, key, None)
    if isinstance(current, bool):
        return bool(value)
    if isinstance(current, int) and not isinstance(current, bool):
        # X position can be "center" string OR an integer
        if isinstance(value, str) and value.strip().lower() == "center":
            return "center"
        try:
            return int(value)
        except (TypeError, ValueError):
            return value
    if isinstance(current, float):
        try:
            return float(value)
        except (TypeError, ValueError):
            return value
    if isinstance(current, str):
        # POS_X fields default to "center" but accept integers as strings too
        if key.endswith("_POS_X") and isinstance(value, (int, float)):
            return int(value)
        return str(value)
    return value


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/config")
def get_config():
    values = current_config_values()
    return jsonify({
        **values,
        "_video_duration": VIDEO_DURATION,
        "_default_at_time": default_frame_time(),
        "_video_csv_filename": Path(config.VIDEO_CSV_PATH).name,
        "_image_csv_filename": Path(config.IMAGE_CSV_PATH).name,
    })


@app.route("/fonts")
def list_fonts():
    base = Path(__file__).parent
    fonts = []
    for path in sorted(FONT_DIR.rglob("*")):
        if path.suffix.lower() in (".ttf", ".otf"):
            rel = str(path.relative_to(base))
            stem = re.sub(r"-[A-Fa-f0-9]{10,}$", "", path.stem)
            name = stem.replace("-", " ").replace("_", " ").title()
            fonts.append({"name": name, "path": rel})
    return jsonify(fonts)


@app.route("/preview", methods=["POST"])
def preview():
    if VIDEO_CLIP is None:
        return jsonify({"error": "Video not loaded"}), 500

    data = request.get_json() or {}
    name = data.get("name") or "Sample Name"
    table_no = data.get("table_no") or "T1"
    at_time = data.get("at_time")
    try:
        at_time = float(at_time) if at_time is not None else default_frame_time()
    except (TypeError, ValueError):
        at_time = default_frame_time()
    raw_overrides = data.get("overrides") or {}
    overrides = {k: coerce_value(k, v) for k, v in raw_overrides.items() if k in UI_KEYS}
    if "FONT_FILENAME" in overrides:
        overrides["FONT_PATH"] = str(Path(__file__).parent / overrides["FONT_FILENAME"])

    frame = get_frame_at(at_time).copy()
    img = generate_preview_image(
        name=name,
        table_no=table_no,
        overrides=overrides,
        base_frame=frame,
        draw_anchors=True,
    )

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")


@app.route("/save", methods=["POST"])
def save():
    data = request.get_json() or {}
    updates = {k: coerce_value(k, v) for k, v in data.items() if k in UI_KEYS}
    if not updates:
        return jsonify({"status": "error", "message": "No valid fields provided"}), 400
    try:
        backup_path = rewrite_config(updates)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "ok", "backup": backup_path, "saved": updates})


@app.route("/inputs")
def list_inputs():
    input_dir = Path(__file__).parent / "input"
    csvs = sorted(p.name for p in input_dir.glob("*.csv")) if input_dir.exists() else []
    return jsonify(csvs)


@app.route("/run", methods=["POST"])
def start_run():
    data = request.get_json() or {}
    job_type = data.get("type")
    csv_filename = data.get("csv", "").strip()
    output_path = data.get("output", "").strip()

    if job_type not in ("video", "image"):
        return jsonify({"error": "type must be 'video' or 'image'"}), 400
    if not csv_filename:
        return jsonify({"error": "csv is required"}), 400

    base = Path(__file__).parent
    csv_path = str(base / "input" / csv_filename)
    if not Path(csv_path).exists():
        return jsonify({"error": f"CSV not found: {csv_filename}"}), 400

    if not output_path:
        output_path = config.VIDEO_OUTPUT_PATH if job_type == "video" else config.IMAGE_OUTPUT_ZIP_PATH
    elif not Path(output_path).is_absolute():
        output_path = str(base / output_path)

    job_id = uuid.uuid4().hex[:8]
    _jobs[job_id] = {"status": "running", "lines": []}

    script = "generate_video_banners.py" if job_type == "video" else "generate_image_cards.py"

    def _run():
        try:
            proc = subprocess.Popen(
                [sys.executable, str(base / script), "--csv", csv_path, "--output", output_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(base),
            )
            for line in proc.stdout:
                _jobs[job_id]["lines"].append(line.rstrip())
            proc.wait()
            _jobs[job_id]["status"] = "done" if proc.returncode == 0 else "error"
        except Exception as exc:
            _jobs[job_id]["lines"].append(f"Launch error: {exc}")
            _jobs[job_id]["status"] = "error"

    threading.Thread(target=_run, daemon=True).start()
    return jsonify({"job_id": job_id})


@app.route("/run/<job_id>")
def poll_run(job_id):
    job = _jobs.get(job_id)
    if not job:
        return jsonify({"error": "job not found"}), 404
    return jsonify(job)


@app.route("/progress")
def get_progress():
    try:
        with open(config.PROGRESS_FILE_PATH) as f:
            import json
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({})


@app.route("/pause", methods=["POST"])
def pause_run():
    ProgressTracker.pause()
    return jsonify({"status": "paused"})


@app.route("/resume", methods=["POST"])
def resume_run():
    ProgressTracker.resume()
    return jsonify({"status": "resumed"})


def main():
    global VIDEO_CLIP, VIDEO_DURATION
    print("Loading video template…")
    VIDEO_CLIP, VIDEO_DURATION = open_clip()
    initial_t = default_frame_time()
    initial_frame = get_frame_at(initial_t)
    print(f"Video loaded: {initial_frame.size[0]}x{initial_frame.size[1]}, "
          f"duration {VIDEO_DURATION:.2f}s, initial frame @ t={initial_t:.2f}s")
    # Default 5001 — macOS reserves 5000 for AirPlay Receiver. Override via PORT env var.
    port = int(os.environ.get("PORT", "5001"))
    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
