import csv


class DigitalCard:
    """A simple class to represent a digital card."""

    def __init__(self, id, name, table_number, language, branch):
        self.id = id
        self.name = name
        self.table_number = table_number
        self.language = language
        self.branch = branch

    def __repr__(self):
        return f"DigitalCard(Id: {self.id}, Name: {self.name}, Table No: {self.table_number}, Language: {self.language}, Branch: {self.table_number})"

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_table_number(self):
        return self.table_number

    def get_language(self):
        return self.language

    def get_branch(self):
        return self.branch


class DigitalCardGenerator:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.cards = []

    def read_csv_and_generate_cards(self, start_id=1):
        with open(self.csv_file_path, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row["id"]) >= start_id:
                    # "branch" or "location" are both accepted as the grouping column
                    raw_branch = row.get("branch") or row.get("location") or ""
                    branch = raw_branch.strip()
                    self.cards.append(
                        DigitalCard(
                            row["id"],
                            row["name"],
                            row["table_no"],
                            row.get("language", ""),
                            branch,
                        )
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
