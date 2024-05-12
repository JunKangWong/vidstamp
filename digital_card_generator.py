import csv

class DigitalCard:
    """A simple class to represent a digital card."""
    def __init__(self, name, table_number):
        self.name = name
        self.table_number = table_number

    def __repr__(self):
        return f"DigitalCard(Name: {self.name}, Table No: {self.table_number})"
    
    def get_name(self):
        return self.name
    
    def get_table_number(self):
        return self.table_number

class DigitalCardGenerator:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.cards = []

    def read_csv_and_generate_cards(self):
        """Reads the CSV file and generates a list of DigitalCard objects."""
        with open(self.csv_file_path, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.cards.append(DigitalCard(row['Name'], row['Table No']))

    def get_digital_cards(self):
        """Returns the list of digital cards."""
        return self.cards

# Example Usage
if __name__ == "__main__":
    generator = DigitalCardGenerator("./input/namelist.csv")
    generator.read_csv_and_generate_cards()
    cards = generator.get_digital_cards()
    for card in cards:
        print(card)
