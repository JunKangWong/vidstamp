from digital_card_generator import DigitalCardGenerator
from digital_video_banner_creator_v5 import DigitalVideoBannerGenerator


class DigitalVideoBannerProcessor:
    def __init__(self, data_source):
        self.digital_cards = self.load_digital_cards(data_source)

    def load_digital_cards(self, input_path):
        cardsGenerator = DigitalCardGenerator(input_path)
        cardsGenerator.read_csv_and_generate_cards()
        return cardsGenerator.get_digital_cards()

    ## TODO: validate if digital cards are unique...

    def generate_digital_banner(self):        
        bannerGenerator = DigitalVideoBannerGenerator()
        bannerGenerator.process_videos(self.digital_cards)


if __name__ == "__main__":
    processor = DigitalVideoBannerProcessor(data_source="./input/sample_namelist2.csv")
    print(processor.digital_cards)
    
    processor.generate_digital_banner()
