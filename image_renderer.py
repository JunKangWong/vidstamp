from PIL import Image, ImageFont, ImageDraw
from config import IMAGE_NAME_FONT_SIZE, IMAGE_TABLE_FONT_SIZE, IMAGE_TEXT_BOTTOM_PADDING

class ImageTextDrawer:
    def __init__(self, image_path, font_path, font_size=IMAGE_NAME_FONT_SIZE):
        self.image_path = image_path
        self.font_path = font_path
        self.font_size = font_size
        self.image = Image.open(self.image_path)
        self.width, self.height = self.image.size
        self.font = ImageFont.truetype(self.font_path, self.font_size)
        self.font2 = ImageFont.truetype(self.font_path, IMAGE_TABLE_FONT_SIZE)
        self.draw = ImageDraw.Draw(self.image)

    def load_image(self):
        """Load the image from the specified path."""
        self.image = Image.open(self.image_path)
        self.width, self.height = self.image.size
        self.draw = ImageDraw.Draw(self.image)

    def add_text(self, text, height, text_color=(0, 0, 0)):
        """
        Draws the specified text on the image at the given position and color.

        :param text: The text to draw.
        :param position: A tuple indicating where to draw the text on the image.
        :param text_color: The color of the text.
        """
        x0, top, x1, _ = self.draw.textbbox((0, 0), text, font=self.font)
        width = (self.width - (x1 - x0)) / 2
        self.draw.text((width, height - top - IMAGE_TEXT_BOTTOM_PADDING), text, fill=text_color, font=self.font)
    
    def add_table_no(self, text, height, text_color=(0, 0, 0)):
        """
        Draws the specified text on the image at the given position and color.

        :param text: The text to draw.
        :param position: A tuple indicating where to draw the text on the image.
        :param text_color: The color of the text.
        """
        table_no = "Table No: {}".format(text)
        x0, top, x1, _ = self.draw.textbbox((0, 0), table_no, font=self.font2)
        width = (self.width - (x1 - x0)) / 2
        self.draw.text((width, height - top - IMAGE_TEXT_BOTTOM_PADDING), table_no, fill=text_color, font=self.font2)
        
    def save_image(self, output_path):
        """
        Saves the modified image to the specified path.

        :param output_path: Path where the modified image will be saved.
        """
        self.image.save(output_path)

    def show_image(self):
        """ 
        Displays the image.
        """
        self.image.show()

# Example Usage
if __name__ == "__main__":
    drawer = ImageTextDrawer("./template/trr_invitation.png", "./font/BASKVILL.ttf")
    drawer.add_text("Mr. John", 1125)
    drawer.add_table_no("T2", 1300)
    drawer.save_image("./output/sample.png")
    drawer.show_image()
