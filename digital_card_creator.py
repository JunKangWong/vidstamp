import os
from digital_card_generator import DigitalCardGenerator
from image_text_drawer import ImageTextDrawer
from PIL import Image, ImageFont, ImageDraw
import zipfile


class DigitalCardImageGenerator(DigitalCardGenerator):
    def __init__(self, csv_file_path, image_template_path, font_path, output_zip_path, font_size=100):
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
                self.image_drawer.add_text(card.name, 1125)
                self.image_drawer.add_table_no(card.table_number, 1300)
                img_temp_path = f"/tmp/card_{i}.png"
                self.image_drawer.image.save(img_temp_path)
                zipf.write(img_temp_path, arcname=os.path.basename(img_temp_path))
                os.remove(img_temp_path)  # Clean up the temporary file

# Example Usage
if __name__ == "__main__":
    generator = DigitalCardImageGenerator(
        csv_file_path="./input/sample_namelist.csv",
        image_template_path="./template/trr_invitation.png",
        font_path="./font/BASKVILL.ttf",
        output_zip_path="./output/digital_cards.zip"
    )
    generator.generate_and_zip_cards()
    print(f"Digital cards have been generated and saved to: {generator.output_zip_path}")
