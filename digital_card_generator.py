import csv


class DigitalCard:
    """A simple class to represent a digital card."""

    def __init__(self, id, name, table_number):
        # TODO: add an id row for the excel, to give each records an id for debugging purposes. so that we can begin from where we left off and implement the capability to start off where we stopped from the csv reader..
        self.id = id
        self.name = name
        self.table_number = table_number

    def __repr__(self):
        return f"DigitalCard(Id: {self.id}, Name: {self.name}, Table No: {self.table_number})"

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_table_number(self):
        return self.table_number


class DigitalCardGenerator:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.cards = []

    # def read_csv_and_generate_cards(self):
    #     """Reads the CSV file and generates a list of DigitalCard objects."""
    #     with open(self.csv_file_path, mode="r", newline="") as file:
    #         reader = csv.DictReader(file)
    #         for row in reader:
    #             self.cards.append(DigitalCard(row["Id"], row["Name"], row["Table No"]))

    def read_csv_and_generate_cards(self, start_id=1):  # Add start_id parameter
        with open(self.csv_file_path, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row["Id"]) >= start_id:  # Start from specified ID
                    self.cards.append(
                        DigitalCard(row["Id"], row["Name"], row["Table No"])
                    )

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
