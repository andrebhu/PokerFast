from random import shuffle

from .deck import Deck
from .player import Player

# States: waiting, preflop, flop, turn, river, showdown
# Actions: bet, call, check, fold


def checkHand(cards):
    """Given five cards, return the best hand"""

    assert len(cards) == 5

    # Sort cards by value and get suits and values
    sorted_cards = sorted(cards, key=lambda card: card.value)
    suits = [card.suit for card in sorted_cards]
    values = [card.value for card in sorted_cards]

    # Check for special hands
    isStraight = True

    for i in range(1, len(values)):
        if values[i] != values[i - 1] + 1:
            isStraight = False
            break

    isFlush = len(set(suits)) == 1
    isRoyalFlush = isStraight and isFlush and values[0] == 10
    isStraightFlush = isStraight and isFlush
    isFourOfAKind = len(set(values)) == 2 and (values[1] == values[2] == values[3])
    isFullHouse = len(set(values)) == 2 and (
        values[0] == values[1] == values[2] or values[2] == values[3] == values[4]
    )

    # AAABC, BAAAC, BCAAA
    isThreeOfAKind = len(set(values)) == 3 and (
        values[0] == values[1] == values[2]
        or values[1] == values[2] == values[3]
        or values[2] == values[3] == values[4]
    )

    # AABBC, AACBB, CAABB
    isTwoPair = len(set(values)) == 3 and (
        values[0] == values[1]
        and values[2] == values[3]
        or values[0] == values[1]
        and values[3] == values[4]
        or values[1] == values[2]
        and values[3] == values[4]
    )

    # Return hand
    if isRoyalFlush:
        return ("royal_flush", values[4])
    elif isStraightFlush:
        return ("straight_flush", values[4])
    elif isFourOfAKind:
        return ("four_of_a_kind", values[2])
    elif isFullHouse:
        return ("full_house", values[2])
    elif isFlush:
        return ("flush", values[4])
    elif isStraight:
        return ("straight", values[4])
    elif isThreeOfAKind:
        return ("three_of_a_kind", values[2])
    elif isTwoPair:
        return ("two_pair", values[3])
    elif len(set(values)) == 4:
        return ("one_pair", values[2])
    else:
        return ("high_card", values[4])


class Game:
    MAX_PLAYERS = 9

    def __init__(self, blinds=[1, 2]):
        self.action_position = 0
        self.dealer_position = 0
        self.deck = Deck(_shuffle=True)
        self.community_cards = []
        self.current_bet = 0
        self.pot = 0

        self.blinds = blinds
        self.heads_up = False
        self.players = []
        self.state = "waiting"

    # Game settings
    def set_blinds(self, small_blind, big_blind):
        """Set blinds"""
        if small_blind >= big_blind:
            raise Exception("Small blind must be less than big blind")
        elif small_blind <= 0 or big_blind <= 0:
            raise Exception("Blinds must be greater than zero")

        self.blinds = [small_blind, big_blind]

    def shuffle_players(self):
        """Shuffle player positions"""
        if len(self.players) > 2:
            shuffle(self.players)

    def add_player(self, name, chips):
        """Add player to game"""
        num_players = len(self.players)
        if num_players == self.MAX_PLAYERS:
            raise Exception("Max players reached")

        self.players.append(Player(name, chips))

    def set_player_balance(self, name, chips):
        """Set player balance"""
        p = self.get_player(name)[0]
        if p:
            p.chips = chips

    def get_player(self, name):
        """Get player and index"""
        for i in range(len(self.players)):
            if self.players[i].name == name:
                return (self.players[i], i)
        raise Exception("Player not found")

    def remove_player(self, name):
        """Remove player from game"""
        for player in self.players:
            if player.name == name:
                self.players.remove(player)
                break


    # Player actions
    def bet(self, name, amount):
        player, position = self.get_player(name)

        if amount > player.chips:
            raise Exception("Not enough chips")
        
        if amount < self.blinds[1]:
            raise Exception("Bet must be greater than big blind")

        if amount < self.current_bet * 2:
            raise Exception("Bet must be two times greater than current bet")
        
        player.chips -= amount
        self.pot += amount
        self.current_bet = amount
        self.action_position = (position + 1) % len(self.players)
        

    def call(self, name):
        pass

    def check(self, name):
        pass

    def fold(self, name):
        pass

    # Game functions
    def start_game(self):
        if len(self.players) < 2:
            raise Exception("Not enough players")

        if len(self.players) == 2:
            self.heads_up = True
        
        self.state = "preflop"
        self.start_preflop(deal=True)


    def start_preflop(self, deal=True):
         # Deal players
        if deal:
            self.deck = Deck(_shuffle=True)
            for player in self.players:
                player.hand = self.deck.deal(2)        

        # Set action position
        if self.heads_up:
            self.action_position = self.dealer_position
        else:
            self.action_position = (self.dealer_position + 3) % len(self.players)

        
        
