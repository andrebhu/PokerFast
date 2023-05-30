class Player:
    def __init__(self, name: str, chips: int=0):
        self.name = name
        self.chips = chips
        
        self.active = False
        self.hand = None

    def __repr__(self):
        return f"Player({self.name}, {self.chips}, {self.hand})"