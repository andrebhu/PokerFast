from random import shuffle
from .card import Card

# Values: 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14
# Suits: s, h, c, d

class Deck:
    def __init__(self, _shuffle=False):
        self.cards = []
        
        for suit in ["s", "h", "c", "d"]:
            for value in range(2, 15):
                self.cards.append(Card(value, suit))
        
        if _shuffle:
            self.shuffle_cards()
        
    def shuffle_cards(self):
        shuffle(self.cards)

    def deal(self, n: int):
        return [self.cards.pop() for _ in range(n)]
    
    def __repr__(self):
        return f"Deck({self.cards})"
