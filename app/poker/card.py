class Card:
    def __init__(self, value: int, suit: str):
        self.value = value
        self.suit = suit

    def __repr__(self):
        return f"{self.value}{self.suit}"