from PIL import Image, ImageFont, ImageDraw

class ImageTextDrawer:
    def __init__(self, image_path, font_path, font_size=100):
        self.image_path = image_path
        self.font_path = font_path
        self.font_size = font_size
        self.image = Image.open(self.image_path)
        self.font = ImageFont.truetype(self.font_path, self.font_size)
        self.draw = ImageDraw.Draw(self.image)

    def add_text(self, text, position, text_color=(0, 0, 0)):
        """
        Draws the specified text on the image at the given position and color.

        :param text: The text to draw.
        :param position: A tuple indicating where to draw the text on the image.
        :param text_color: The color of the text.
        """
        self.draw.text(position, text, fill=text_color, font=self.font)

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
    drawer = ImageTextDrawer("./template/certificate_template2.jpg", "./font/Themundayfreeversion-Regular.ttf")
    drawer.add_text("Anderson Wong", (320, 1700))
    drawer.save_image("./output/text_added.png")
    drawer.show_image()
