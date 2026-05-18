import argparse
import os
import zipfile
from card_model import DigitalCardGenerator
from image_renderer import ImageTextDrawer
from config import IMAGE_CSV_PATH, IMAGE_TEMPLATE_PATH, FONT_PATH, IMAGE_OUTPUT_ZIP_PATH, IMAGE_NAME_Y, IMAGE_TABLE_Y


class DigitalCardImageGenerator(DigitalCardGenerator):
    def __init__(self, csv_file_path, image_template_path, font_path, output_zip_path):
        super().__init__(csv_file_path)
        self.image_drawer = ImageTextDrawer(image_path=image_template_path, font_path=font_path)
        self.image_template_path = image_template_path
        self.output_zip_path = output_zip_path

    def generate_and_zip_cards(self):
        """Generates digital card images and saves them directly into a zip file."""
        with zipfile.ZipFile(self.output_zip_path, 'w') as zipf:
            self.read_csv_and_generate_cards()
            for i, card in enumerate(self.cards, start=1):
                self.image_drawer.load_image()  # Reload the template image for each card
                self.image_drawer.add_text(card.name, IMAGE_NAME_Y)
                self.image_drawer.add_table_no(card.table_number, IMAGE_TABLE_Y)
                img_temp_path = f"/tmp/card_{i}.png"
                self.image_drawer.image.save(img_temp_path)
                zipf.write(img_temp_path, arcname=os.path.basename(img_temp_path))
                os.remove(img_temp_path)  # Clean up the temporary file

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default=IMAGE_CSV_PATH)
    parser.add_argument("--output", default=IMAGE_OUTPUT_ZIP_PATH)
    args = parser.parse_args()

    generator = DigitalCardImageGenerator(
        csv_file_path=args.csv,
        image_template_path=IMAGE_TEMPLATE_PATH,
        font_path=FONT_PATH,
        output_zip_path=args.output,
    )
    generator.generate_and_zip_cards()
    print(f"Done. Cards saved to: {generator.output_zip_path}")
