# Digital Card Generator

Batch-generates personalized event videos and image cards from a CSV attendee list. Give it a name/table-number list and a video or image template, and it stamps each attendee's details onto their own copy — a per-attendee digital place card or video banner. It solves one specific problem: without a preview step, "is the text in the right spot" means re-encoding a full video just to find out the name sits 40px too low. This repo lets you check placement on a single extracted frame first, for free.

There are two ways to run it: a local web UI (`app.py`, recommended) and a pair of CLI scripts (`generate_video_banners.py`, `generate_image_cards.py`) that the UI itself shells out to.

## Security note

`app.py` has **no authentication**. `/save` rewrites `config.py` on disk, and `/run` / `/run-single` spawn subprocesses that write video/image files to your filesystem. Anyone who can reach the port can trigger both. It is built to run on `127.0.0.1` for a single local user — do not expose it on a public interface, reverse proxy, or shared network without adding your own auth layer in front of it.

---

## Prerequisites

- **Python 3.9+**
- **ffmpeg installed and on your `PATH`.** moviepy shells out to it for every video render; without it, video banner generation and the preview tool will fail.
- **A font file** (`.ttf`/`.otf`) of your choosing. None ship with this repo — check the licence of whatever you use before redistributing it.
- **A video template** (for video banners) and/or **image template** (for image cards). None ship with this repo either — these are normally client-branded assets you supply per event.

Install Python dependencies:

```bash
pip install -r requirements.txt
```

(`requirements.txt` covers Pillow, moviepy, and Flask.)

---

## Web UI

```bash
python3 app.py
# open http://localhost:5001
```

(Port defaults to `5001` because macOS reserves `5000` for AirPlay Receiver. Override with `PORT=5000 python3 app.py`.)

The UI has two tabs, **Video Banner** and **Image Card**, matching the two CLI modes below. Whatever tab is active determines which config keys the right-hand preview and the Save button act on.

**Live preview.** Every field you touch — position, font, size, casing, colour, entrance time — triggers a debounced call to `/preview`, which redraws the sample name and table number onto a single cached video frame (or the image template) and sends back a PNG. No video is encoded and no file is written until you explicitly run a job. Red crosshairs mark each text element's exact anchor point.

**Per-card overrides.** The "Single Card" panel lets you load a CSV (via the Input CSV dropdown), search/select one attendee row, and tweak position, font, size, casing, colour, and pixel format *just for that row* without touching the shared config. Hitting "Generate This Card" runs `generate_video_banners.py --single-id <id>` with those overrides passed through — it does not disturb the batch resume cursor. "Use sample text" clears the selection and goes back to the generic Sample Text fields.

**Batch runs, pause/resume, and ID ranges.** "Generate Videos" / "Generate Image Cards" spawn the corresponding script as a subprocess and poll it for log output. For video runs, a progress bar polls `/progress` (total/done/percentage/ETA/current name). Pause and Resume call `/pause` and `/resume`, which create or remove a sentinel file the batch processor checks between attendees — it finishes the current video, then blocks until resumed. The "Range (inclusive)" fields map to `--from-id`/`--to-id`: leave both blank to resume from wherever the last run left off (or start at row 1 on a fresh CSV), or set explicit bounds to (re)run a subset. Setting "From" also resets the resume cursor to that ID.

**Save writes to `config.py`.** Clicking "Save to config.py" backs up the current file to `./output/config_backup/config_<timestamp>.py`, then rewrites only the changed lines via regex — comments and formatting elsewhere in the file are left untouched. The response shows the backup path so you can diff or roll back.

Routes, if you're integrating against this instead of clicking through it: `/config` (GET current values + video metadata), `/inputs` (list CSVs in `./input/`), `/cards?csv=` (parsed rows for the Single Card list), `/fonts` (fonts found under `./font/`), `/video-templates` (MP4s found under `./template/`), `/preview` (POST, returns a PNG), `/run` and `/run-single` (POST, start a batch or single-card job and return a `job_id`), `/run/<job_id>` (poll status/log lines), `/progress`, `/pause`, `/resume`, and `/save`.

---

## CLI: Mode 1 — Image Cards

### Step 1 — Prepare your CSV

Place a CSV file in `./input/` with these columns:

```
id,name,table_no,language,branch
1,JANE DOE,12,C,ACME
2,Alex Tan,12,C,ACME
```

### Step 2 — Place your assets

- Image template (PNG/JPG) → `./template/`
- Your font file → `./font/`

### Step 3 — Configure `config.py`

Set `IMAGE_CSV_PATH`, `IMAGE_TEMPLATE_PATH`, `FONT_FILENAME`, and `IMAGE_OUTPUT_ZIP_PATH`.

### Step 4 — Run

```bash
python3 generate_image_cards.py
```

**Output:** a ZIP at `IMAGE_OUTPUT_ZIP_PATH` (default `./output/digital_cards.zip`) containing `card_1.png`, `card_2.png`, etc., one per CSV row.

---

## CLI: Mode 2 — Video Banners

### Step 1 — Prepare your assets

- CSV with `id,name,table_no` (plus optional `language`, `branch`/`location`) → `./input/`
- Source MP4 video template(s) → `./template/`

### Step 2 — Configure `config.py`

Set `VIDEO_CSV_PATH`, `VIDEO_INPUT_PATH`, `FONT_FILENAME`, `VIDEO_EN_FILENAME`, and `VIDEO_CN_FILENAME`.

### Step 3 — Preview text positions (optional but recommended)

Before batch generating, use the preview tool to visually verify where name and table number will appear:

```bash
# Preview using the first row from your CSV at the default frame time
python3 preview_positions.py

# Preview at a specific second (useful when text fades in later in the video)
python3 preview_positions.py --at 10

# Preview with a custom name and table number
python3 preview_positions.py "Jane Doe" T5 --at 10.5
```

This extracts a single frame from the template video, draws the text overlays on it, and saves the result to `./output/preview.png` — no video encoding needed. Adjust `VIDEO_NAME_POS_Y`, `VIDEO_TABLE_POS_Y`, and font sizes in `config.py`, then re-run until the positions look right. This is the same mechanism the web UI's live preview uses under the hood.

### Step 4 — Run the batch processor

```bash
python3 generate_video_banners.py
```

Useful flags: `--csv <path>`, `--output <path>`, `--from-id N` / `--to-id N` (inclusive range), `--single-id N` (render one attendee without touching the resume cursor), `--overrides <json>` (per-run config overrides, same mechanism the web UI's Single Card panel uses).

**Output:** `./output/digital_video_banner/{branch}/T{table_no}_{name}.mp4` — one video per attendee, organized by branch (or `location` column if `branch` is absent).

The processor supports **resuming**: it saves the last processed ID to `./output/log/last_processed_id.txt`, keyed to the CSV path it was run against, so an interrupted run continues from where it left off the next time you run the same CSV. Create `./output/log/PAUSE` (or click Pause in the UI) to pause between attendees; remove it (or click Resume) to continue.

---

## Configuration reference

All tunable values live in `config.py`. Keys marked **UI** are editable from the web UI and get written back on Save; everything else is config.py-only.

**Paths**

| Setting | UI | What it controls |
|---|---|---|
| `VIDEO_CSV_PATH` | UI | Input CSV for video generation |
| `IMAGE_CSV_PATH` | UI | Input CSV for image card generation |
| `IMAGE_TEMPLATE_PATH` | — | Image template file drawn on for each card |
| `VIDEO_INPUT_PATH` | — | Directory containing source MP4 templates (defaults to `./template/`) |
| `FONT_FILENAME` / `FONT_PATH` | UI | Font used for both image and video text overlays (`FONT_FILENAME` is the editable relative path; `FONT_PATH` is derived) |
| `VIDEO_OUTPUT_PATH` | UI | Root output directory for video banners, one subfolder per branch |
| `IMAGE_OUTPUT_ZIP_PATH` | UI | Output ZIP path for image cards |
| `VIDEO_EN_FILENAME` / `VIDEO_CN_FILENAME` | UI (via template selector) | Source video per `language` value (`E` vs anything else) |
| `LOG_DIR` and derived paths | — | Resume cursor, pause sentinel, progress JSON, and log file location |

**Video — positioning & text**

| Setting | UI | What it controls |
|---|---|---|
| `VIDEO_NAME_POS_X` / `VIDEO_NAME_POS_Y` | UI | Name text position (`"center"` or a pixel offset; Y negative = offset from bottom) |
| `VIDEO_TABLE_POS_X` / `VIDEO_TABLE_POS_Y` | UI | Table number text position |
| `VIDEO_NAME_CASING` / `VIDEO_TABLE_CASING` | UI | `title` / `upper` / `lower` / `as-is` |
| `VIDEO_TABLE_PREFIX` | UI | Text prepended to the table number (e.g. `"Table Number:"`) |
| `VIDEO_TABLE_PREFIX_SPACING` | UI | Spaces between prefix and number |
| `VIDEO_TABLE_NUMBER_FORMAT` | UI | `as-is` / `number` (digits only) / `padded` (zero-padded) |
| `VIDEO_FONT_COLOR` | UI | Text colour for both overlays |
| `VIDEO_TEXT_MARGIN` | UI | Vertical padding added around each text clip's canvas (prevents descender clipping) |
| `VIDEO_TEXT_ENTRANCE_TIME` | UI | Delay (s) before overlays appear |
| `VIDEO_TEXT_DURATION` | — | How long overlays stay visible (s) |
| `VIDEO_TEXT_FADE_DURATION` | — | Crossfade-in duration (s) |

**Video — font sizing**

| Setting | UI | What it controls |
|---|---|---|
| `VIDEO_NAME_FONT_SIZE` | UI | Maximum name font size |
| `VIDEO_NAME_FONT_SIZE_MIN` | UI | Minimum name font size before giving up shrinking |
| `VIDEO_NAME_FONT_SIZE_STEP` | UI | Point decrement per shrink iteration |
| `VIDEO_NAME_AUTOFIT` | UI (Single Card only) | Auto-shrink long names to fit `VIDEO_NAME_MAX_WIDTH` |
| `VIDEO_NAME_MAX_WIDTH` | UI | Max pixel width before the name is shrunk |
| `VIDEO_NAME_MARGIN` | UI | Side margin subtracted from the max-width zone |
| `VIDEO_TABLE_FONT_SIZE` | UI | Table number font size |

**Video — encoding**

| Setting | UI | What it controls |
|---|---|---|
| `VIDEO_PIXEL_FORMAT` | UI | `yuv420p` (compatible) or `yuv444p` (higher colour depth, less compatible) |
| `VIDEO_CODEC` / `VIDEO_AUDIO_CODEC` | — | ffmpeg codecs used for output |
| `VIDEO_BITRATE` | — | Output video bitrate |

**Image cards**

| Setting | UI | What it controls |
|---|---|---|
| `IMAGE_NAME_Y` / `IMAGE_TABLE_Y` | UI | Vertical pixel position of each text element |
| `IMAGE_NAME_FONT_SIZE` / `IMAGE_TABLE_FONT_SIZE` | UI | Font sizes |
| `IMAGE_TEXT_BOTTOM_PADDING` | UI | Pixels to shift text upward (fixes clipped descenders) |

---

## CSV column reference

| Column | Required by | Description |
|---|---|---|
| `id` | both | Sequential integer, used for resume support and as the Single Card / `--single-id` key |
| `name` | both | Attendee name, drawn onto the card or video |
| `table_no` | both | Table number |
| `language` | video only | `E` = English video, anything else (including blank) = the "CN" video |
| `branch` | video only | Organizes video output into subfolders (also accepts a `location` column) |

---

## Project structure

```
app.py                       Web UI + Flask routes (start here)
templates/index.html         Web UI front end
config.py                    All tunable settings, read by everything else
generate_image_cards.py      CLI entry point: image card generation
generate_video_banners.py    CLI entry point: video banner generation
preview_positions.py         Single-frame preview without encoding a video
video_renderer.py            Core video rendering logic
image_renderer.py            Core image rendering logic
card_model.py                CSV reader and data model
progress_tracker.py          Progress JSON + pause/resume sentinel
logging_utils.py             Timing decorators and file logging
./input/                     CSV files (gitignored except a sample)
./template/                  Video/image templates you supply (gitignored)
./font/                      Font files you supply (gitignored)
./output/                    Generated cards, videos, logs, config backups (gitignored)
./output/log/                Resume state, pause sentinel, progress.json
```

---

## Licence

No `LICENSE` file exists in this repository yet. Add one before treating this as open source — MIT is a reasonable default for a project like this.
