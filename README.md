# Digital Card Generator

Generates personalized event cards from a CSV list. Two modes: **image cards** (PNG in a ZIP) and **video banners** (MP4 per attendee).

## Dependencies

```bash
pip install Pillow moviepy
```

Requires Python 3.12+.

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
- Font file → `./font/BASKVILL.ttf`

### Step 3 — Configure `digital_card_creator.py`

Edit the `if __name__ == "__main__"` block at the bottom of the file:

```python
generator = DigitalCardImageGenerator(
    csv_path="./input/your_namelist.csv",
    template_path="./template/trr_invitation.png",
    font_path="./font/BASKVILL.ttf",
    output_zip_path="./output/digital_cards.zip"
)
generator.generate_cards()
```

### Step 4 — Run

```bash
python digital_card_creator.py
```

**Output:** `./output/digital_cards.zip` containing `card_1.png`, `card_2.png`, etc., one per CSV row.

---

## Mode 2: Video Banners

### Step 1 — Fix hardcoded paths

Three files contain old hardcoded paths (`/Users/junkangwong/...`) that must be updated before use:

- `digital_video_banner_creator_v5.py` — input/output paths
- `digital_video_banner_creator_csv.py` — CSV and output paths
- `utility.py` — log file path

### Step 2 — Prepare your assets

- CSV with `id,name,table_no,language,branch` → `./input/`
- Two source MP4s → `./input/`:
  - `TRR_E_Invitation_EN_S.mp4` (for `language=E`)
  - `TRR_E_Invitation_CN_S.mp4` (for `language=C`)

### Step 3 — Run the batch processor

```bash
python digital_video_banner_creator_csv.py
```

**Output:** `./output/digital_video_banner/{branch}/T{table_no}_{name}.mp4` — one video per attendee, organized by branch.

The processor supports **resuming** — it saves the last processed ID so if interrupted, it continues from where it left off.

---

## CSV Column Reference

| Column     | Required by  | Description                                         |
|------------|--------------|-----------------------------------------------------|
| `id`       | both         | Sequential integer, used for resume support         |
| `name`     | both         | Attendee name, drawn onto the card or video         |
| `table_no` | both         | Table number                                        |
| `language` | video only   | `E` = English video, `C` = Chinese video            |
| `branch`   | video only   | Organizes video output into subfolders              |

---

## Project Structure

```
./input/          CSV files and source MP4s
./template/       Image templates (PNG/JPG)
./font/           Font files (.ttf)
./output/         Generated cards and videos
```
