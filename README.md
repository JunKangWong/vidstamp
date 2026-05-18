# Digital Card Generator

Generates personalized event cards from a CSV list. Two modes: **image cards** (PNG in a ZIP) and **video banners** (MP4 per attendee).

## Dependencies

```bash
pip install Pillow moviepy
```

Requires Python 3.9+.

---

## Configuration

All tunable values live in **`config.py`** — paths, font sizes, text positions, video encoding settings. Edit this file before running any script.

Key settings:

| Setting | What it controls |
|---|---|
| `VIDEO_CSV_PATH` | Input CSV for video generation |
| `IMAGE_CSV_PATH` | Input CSV for image card generation |
| `VIDEO_INPUT_PATH` | Directory containing source MP4 templates |
| `FONT_PATH` | Font file used for all text overlays |
| `VIDEO_NAME_POS_Y` | Vertical position of name text (negative = offset from bottom) |
| `VIDEO_TABLE_POS_Y` | Vertical position of table number text |
| `VIDEO_TEXT_DURATION` | How long text overlays stay visible (seconds) |
| `VIDEO_EN_FILENAME` / `VIDEO_CN_FILENAME` | Source video files per language |

---

## Mode 1: Image Cards

### Step 1 — Prepare your CSV

Place a CSV file in `./input/` with these columns:

```
id,name,table_no,language,branch
1,HUI JUN HOE,45,C,SSR
2,Liew Ming Hui,45,C,SSR
```

### Step 2 — Place your assets

- Image template (PNG/JPG) → `./template/`
- Font file → `./font/baskvill/BASKVILL.ttf`

### Step 3 — Configure `config.py`

Set `IMAGE_CSV_PATH`, `IMAGE_TEMPLATE_PATH`, and `IMAGE_OUTPUT_ZIP_PATH`.

### Step 4 — Run

```bash
python3 generate_image_cards.py
```

**Output:** `./output/digital_cards.zip` containing `card_1.png`, `card_2.png`, etc., one per CSV row.

---

## Mode 2: Video Banners

### Step 1 — Prepare your assets

- CSV with `id,name,table_no` (plus optional `language`, `branch`/`location`) → `./input/`
- Source MP4 video template(s) → `./template/`

### Step 2 — Configure `config.py`

Set `VIDEO_CSV_PATH`, `VIDEO_INPUT_PATH`, `VIDEO_EN_FILENAME`, and `VIDEO_CN_FILENAME`.

### Step 3 — Preview text positions (optional but recommended)

Before batch generating, use the preview tool to visually verify where name and table number will appear:

```bash
# Preview using the first row from your CSV at the default frame time
python3 preview_positions.py

# Preview at a specific second (useful when text fades in later in the video)
python3 preview_positions.py --at 10

# Preview with a custom name and table number
python3 preview_positions.py "John Smith" T5 --at 10.5
```

This extracts a single frame from the template video, draws the text overlays on it, and opens the result as `./output/preview.png` — no video encoding needed. Adjust `VIDEO_NAME_POS_Y`, `VIDEO_TABLE_POS_Y`, and font sizes in `config.py`, then re-run until the positions look right.

Red crosshairs mark the exact anchor point of each text element.

### Step 4 — Run the batch processor

```bash
python3 generate_video_banners.py
```

**Output:** `./output/digital_video_banner/{branch}/T{table_no}_{name}.mp4` — one video per attendee, organized by branch (or `location` column if `branch` is absent).

The processor supports **resuming** — it saves the last processed ID to `./output/log/last_processed_id.txt` so if interrupted, it continues from where it left off.

---

## CSV Column Reference

| Column       | Required by  | Description                                                   |
|--------------|--------------|---------------------------------------------------------------|
| `id`         | both         | Sequential integer, used for resume support                   |
| `name`       | both         | Attendee name, drawn onto the card or video                   |
| `table_no`   | both         | Table number                                                  |
| `language`   | video only   | `E` = English video, `C` = Chinese video (optional)          |
| `branch`     | video only   | Organizes video output into subfolders (also accepts `location`) |

---

## Project Structure

```
./input/                    CSV files
./template/                 Source MP4 templates and image templates
./font/                     Font files (.ttf)
./output/                   Generated cards, videos, and preview.png
./output/log/               Resume state and processing logs
config.py                   All tunable settings — start here
generate_image_cards.py     Entry point: image card generation
generate_video_banners.py   Entry point: video banner generation
preview_positions.py        Preview text placement without encoding video
video_renderer.py           Core video rendering logic
image_renderer.py           Core image rendering logic
card_model.py               CSV reader and data model
logging_utils.py            Timing decorators and file logging
```
