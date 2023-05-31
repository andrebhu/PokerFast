from .player import Player

# This class helps the Game class keep track of player actions and their chips

class Seat:
    def __init__(self):
        self.last_bet = 0
        self.folded = True
        self.player = None
        self.cards = []
        self.chips = 0


    def __repr__(self):
        return f"Seat({self.player}, {self.chips}, {self.cards})"
