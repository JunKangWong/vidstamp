import os
import csv
from PIL import Image, ImageFont, ImageDraw
import zipfile

class DigitalCardCreator:
    def __init__(self, csv_file_path, image_template_path, font_path, output_directory, font_size=100):
        self.csv_file_path = csv_file_path
        self.image_template_path = image_template_path
        self.font_path = font_path
        self.font_size = font_size
        self.output_directory = output_directory
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
    
    def read_csv_and_generate_cards(self):
        with open(self.csv_file_path, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for i, row in enumerate(reader, start=1):
                self.generate_card_image(row['Name'], row['Phone Number'], f"card_{i}.png")

    def generate_card_image(self, name, phone_number, output_filename):
        image = Image.open(self.image_template_path)
        font = ImageFont.truetype(self.font_path, self.font_size)
        draw = ImageDraw.Draw(image)
        text = f"{name}\n{phone_number}"
        draw.text((320, 1600), text, (0, 0, 0), font=font)
        image.save(os.path.join(self.output_directory, output_filename))
    
    def zip_output_directory(self):
        zip_filename = os.path.join(self.output_directory, "digital_cards.zip")
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.output_directory):
                for file in files:
                    if file.endswith(".png"):
                        zipf.write(os.path.join(root, file), arcname=file)
        return zip_filename

# Example Usage
if __name__ == "__main__":
    creator = DigitalCardCreator(
        csv_file_path="./input/namelist.csv",
        image_template_path="./template/certificate_template2.jpg",
        font_path="./font/Themundayfreeversion-Regular.ttf",
        output_directory="./output"
    )
    creator.read_csv_and_generate_cards()
    zip_file = creator.zip_output_directory()
    print(f"Digital cards created and zipped in: {zip_file}")
