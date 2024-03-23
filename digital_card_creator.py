import csv
import os
from digital_card_generator import DigitalCardGenerator
from image_text_drawer import ImageTextDrawer
from PIL import Image, ImageFont, ImageDraw
import zipfile

class EnhancedImageTextDrawer(ImageTextDrawer):
    def __init__(self, font_path, font_size=100):
        self.font_path = font_path
        self.font_size = font_size

    def create_image_with_text(self, text, image_template_path):
        """Creates an image from a template with the specified text."""
        image = Image.open(image_template_path)
        font = ImageFont.truetype(self.font_path, self.font_size)
        draw = ImageDraw.Draw(image)
        draw.text((50, 150), text, (0, 0, 0), font=font)
        return image

class DigitalCardImageGenerator(DigitalCardGenerator):
    def __init__(self, csv_file_path, image_template_path, font_path, output_zip_path, font_size=100):
        super().__init__(csv_file_path)
        self.image_drawer = EnhancedImageTextDrawer(font_path, font_size)
        self.image_template_path = image_template_path
        self.output_zip_path = output_zip_path

    def generate_and_zip_cards(self):
        """Generates digital card images and saves them directly into a zip file."""
        with zipfile.ZipFile(self.output_zip_path, 'w') as zipf:
            self.read_csv_and_generate_cards()
            for i, card in enumerate(self.cards, start=1):
                image = self.image_drawer.create_image_with_text(f"{card.name}\n{card.phone_number}", self.image_template_path)
                img_temp_path = f"/tmp/card_{i}.png"
                image.save(img_temp_path)
                zipf.write(img_temp_path, arcname=os.path.basename(img_temp_path))
                os.remove(img_temp_path)  # Clean up the temporary file

# Example Usage
if __name__ == "__main__":
    generator = DigitalCardImageGenerator(
        csv_file_path="./input/namelist.csv",
        image_template_path="./template/certificate_template2.jpg",
        font_path="./font/Themundayfreeversion-Regular.ttf",
        output_zip_path="./output/digital_cards.zip"
    )
    generator.generate_and_zip_cards()
    print(f"Digital cards have been generated and saved to: {generator.output_zip_path}")
