import argparse
from card_model import DigitalCardGenerator
from video_renderer import DigitalVideoBannerGenerator
from progress_tracker import ProgressTracker
from config import VIDEO_CSV_PATH, VIDEO_OUTPUT_PATH, LAST_PROCESSED_ID_PATH


class DigitalVideoBannerProcessor:
    def __init__(self, data_source):
        self.digital_cards = self.load_digital_cards(data_source)

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
