import argparse
from PIL import ImageFont
from card_model import DigitalCardGenerator
from video_renderer import DigitalVideoBannerGenerator
from progress_tracker import ProgressTracker
from config import (
    VIDEO_CSV_PATH,
    VIDEO_OUTPUT_PATH,
    LAST_PROCESSED_ID_PATH,
    FONT_PATH,
    VIDEO_NAME_FONT_SIZE_MIN,
    VIDEO_NAME_MAX_WIDTH,
    VIDEO_NAME_CASING,
)


def _warn_overflow_names(cards) -> None:
    font = ImageFont.truetype(FONT_PATH, VIDEO_NAME_FONT_SIZE_MIN)
    overflows = []
    for card in cards:
        raw = card.get_name()
        if VIDEO_NAME_CASING == "upper":
            name = raw.upper()
        elif VIDEO_NAME_CASING == "lower":
            name = raw.lower()
        elif VIDEO_NAME_CASING == "as-is":
            name = raw
        else:
            name = raw.title()
        bbox = font.getbbox(name)
        if (bbox[2] - bbox[0]) > VIDEO_NAME_MAX_WIDTH:
            overflows.append((card.get_id(), name, bbox[2] - bbox[0]))

    if overflows:
        print(
            f"\n⚠  NAME OVERFLOW WARNING — {len(overflows)} name(s) exceed "
            f"{VIDEO_NAME_MAX_WIDTH}px even at minimum font size ({VIDEO_NAME_FONT_SIZE_MIN}pt):"
        )
        for id_, name, px in overflows:
            print(f"  Row {id_:>4} | {name!r:<45} | {px}px")
        print("  Consider shortening these names in the CSV.\n")


class DigitalVideoBannerProcessor:
    def __init__(self, data_source):
        self.digital_cards = self.load_digital_cards(data_source)
        _warn_overflow_names(self.digital_cards)

    def load_digital_cards(self, input_path):
        cardsGenerator = DigitalCardGenerator(input_path)
        try:
            with open(LAST_PROCESSED_ID_PATH, "r") as f:
                start_id = int(f.read()) + 1
        except FileNotFoundError:
            start_id = 1
            with open(LAST_PROCESSED_ID_PATH, "w") as f:
                f.write(str(start_id))

        cardsGenerator.read_csv_and_generate_cards(start_id=start_id)
        return cardsGenerator.get_digital_cards()

    def generate_digital_banner(self, output_path=None):
        bannerGenerator = DigitalVideoBannerGenerator(output_path=output_path)
        tracker = ProgressTracker(total=len(self.digital_cards))
        bannerGenerator.process_videos(self.digital_cards, progress_tracker=tracker)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default=VIDEO_CSV_PATH)
    parser.add_argument("--output", default=VIDEO_OUTPUT_PATH)
    args = parser.parse_args()

    processor = DigitalVideoBannerProcessor(data_source=args.csv)
    print(f"Loaded {len(processor.digital_cards)} cards from {args.csv}")
    processor.generate_digital_banner(output_path=args.output)
