from random import shuffle
from itertools import cycle

from .deck import Deck
from .seat import Seat
from .player import Player


class Game:
    MAX_PLAYERS = 9
    STATES = ["waiting", "preflop", "flop", "turn", "river", "showdown"]
    ACTIONS = ["bet", "call", "check", "fold"]

    def __init__(self, blinds: list = [1, 2]):
        # Round variables
        self.action_seat = None
        self.active_players = 0
        self.deck = Deck(_shuffle=True)
        self.dealer_seat = None
        self.community_cards = []
        self.current_bet = 0
        self.pot = 0
        self.seats = [Seat() for _ in range(self.MAX_PLAYERS)]
        self.seats_cycle = cycle(self.seats)

        # Game variables
        self.blinds = blinds
        self.heads_up = False
        self.players = []
        self.state = "waiting"

    def get_player(self, username):
        """Get player"""
        for i in range(len(self.players)):
            if self.players[i].username == username:
                return self.players[i]

    def add_player(self, username):
        if self.get_player(username):
            raise Exception("Username already exists")

        p = Player(username)
        self.players.append(p)

    def shuffle_seats(self):
        shuffle(self.seats)

    def add_player_to_seat(self, username, chips, i):
        """Add player to seat"""
        assert i < self.MAX_PLAYERS - 1, "Seat index out of range"

        p = self.get_player(username)
        if p:
            if self.seats[i].player == None:
                self.seats[i].player = p
                self.seats[i].chips = chips
                self.active_players += 1
            else:
                raise Exception("Seat is taken")
        else:
            raise Exception("Player not found")

    # TODO: Write function to automatically add all unseated players to
    # available seats

    def get_next_active_player(self):
        """Get the next active player that is not folded"""
        seat = next(self.seats_cycle)

        while seat.folded:
            seat = next(self.seats_cycle)

        return seat

    def pay(self, seat, amount):
        """Pay chips to pot"""
        if amount > seat.chips:
            # TODO: Handle all in and side pots
            raise Exception("Not enough chips")

        seat.chips -= amount
        self.pot += amount

    # Round logic
    def start_round(self):
        """Start round"""

        if self.state != "waiting":
            raise Exception("Round has already started, should not reach here")

        if self.active_players < 2:
            raise Exception("Not enough players")

        # Deal cards with a new deck
        self.deck = Deck(_shuffle=True)
        for seat in self.seats:
            if seat.player:
                seat.folded = False
                seat.cards = self.deck.deal(2)

        # Assign dealer as first active player
        self.dealer_seat = self.get_next_active_player()

        # In a heads-up game, the dealer is the small blind and is first to act
        if self.active_players == 2:
            # Pay small blind
            self.pay(self.dealer_seat, self.blinds[0])

            # Pay big blind
            self.temp_player = self.get_next_active_player()
            self.pay(self.temp_player, self.blinds[1])

            # Dealer is first to act
            self.action_seat = self.dealer_seat

        # In a game with more than two players, the player to the left of the
        # dealer is the small blind
        else:
            # Pay small blind
            self.action_seat = self.get_next_active_player()
            self.pay(self.action_seat, self.blinds[0])

            # Pay big blind
            self.action_seat = self.get_next_active_player()
            self.pay(self.action_seat, self.blinds[1])

            self.action_seat = self.get_next_active_player()

        self.state = "preflop"

    # Controls the game's flow between rounds and player actions
    def update(self):
        """Update game state"""

        if self.active_players <= 1:
            # TODO: End of round
            self.state = "showdown"
            return

        # TODO: Check if all active players have bet the same amount
        # If so, deal a card and move to the next round and update the state

    def fold(self, username):
        """Fold"""
        if self.state not in ["preflop", "flop", "turn", "river"]:
            raise Exception("Game state is not valid")

        # Some type checking
        if isinstance(self.action_seat, Seat) and isinstance(
            self.action_seat.player, Player
        ):
            if self.action_seat.player.username != username:
                raise Exception("Not your turn, shouldn't reach here")
            else:
                self.action_seat.folded = True
                self.active_players -= 1
                self.update()

    # Game settings
    # def set_blinds(self, blinds):
    #     """Set blinds"""
    #     small_blind, big_blind = blinds[0], blinds[1]

    #     if small_blind >= big_blind:
    #         raise Exception("Small blind must be less than big blind")
    #     elif small_blind <= 0 or big_blind <= 0:
    #         raise Exception("Blinds must be greater than zero")

    #     self.blinds = blinds


#     # Player actions
#     def bet(self, name, amount):
#         player, position = self.get_player(name)

#         if amount > player.chips:
#             raise Exception("Not enough chips")

#         if amount < self.blinds[1]:
#             raise Exception("Bet must be greater than big blind")

#         if amount < self.current_bet * 2:
#             raise Exception("Bet must be two times greater than current bet")

#         player.chips -= amount
#         self.pot += amount
#         self.current_bet = amount
#         self.action_position = (position + 1) % len(self.players)

#     def call(self, name):
#         pass

#     def check(self, name):
#         pass

#     def fold(self, name):
#         pass

#     # Game functions
#     def start_game(self):
#         if len(self.players) < 2:
#             raise Exception("Not enough players")

#         if len(self.players) == 2:
#             self.heads_up = True

#         self.state = "preflop"
#         self.start_preflop(deal=True)

#     def start_preflop(self, deal=True):
#         # Deal players
#         if deal:
#             self.deck = Deck(_shuffle=True)
#             for player in self.players:
#                 player.hand = self.deck.deal(2)

#         # Set action position
#         if self.heads_up:
#             self.action_position = self.dealer_position
#         else:
#             self.action_position = (self.dealer_position + 3) % len(self.players)


# def checkHand(cards):
#     """Given five cards, return the best hand"""

#     assert len(cards) == 5

#     # Sort cards by value and get suits and values
#     sorted_cards = sorted(cards, key=lambda card: card.value)
#     suits = [card.suit for card in sorted_cards]
#     values = [card.value for card in sorted_cards]

#     # Check for special hands
#     isStraight = True

#     for i in range(1, len(values)):
#         if values[i] != values[i - 1] + 1:
#             isStraight = False
#             break

#     isFlush = len(set(suits)) == 1
#     isRoyalFlush = isStraight and isFlush and values[0] == 10
#     isStraightFlush = isStraight and isFlush
#     isFourOfAKind = len(set(values)) == 2 and (values[1] == values[2] == values[3])
#     isFullHouse = len(set(values)) == 2 and (
#         values[0] == values[1] == values[2] or values[2] == values[3] == values[4]
#     )

#     # AAABC, BAAAC, BCAAA
#     isThreeOfAKind = len(set(values)) == 3 and (
#         values[0] == values[1] == values[2]
#         or values[1] == values[2] == values[3]
#         or values[2] == values[3] == values[4]
#     )

#     # AABBC, AACBB, CAABB
#     isTwoPair = len(set(values)) == 3 and (
#         values[0] == values[1]
#         and values[2] == values[3]
#         or values[0] == values[1]
#         and values[3] == values[4]
#         or values[1] == values[2]
#         and values[3] == values[4]
#     )

#     # Return hand
#     if isRoyalFlush:
#         return ("royal_flush", values[4])
#     elif isStraightFlush:
#         return ("straight_flush", values[4])
#     elif isFourOfAKind:
#         return ("four_of_a_kind", values[2])
#     elif isFullHouse:
#         return ("full_house", values[2])
#     elif isFlush:
#         return ("flush", values[4])
#     elif isStraight:
#         return ("straight", values[4])
#     elif isThreeOfAKind:
#         return ("three_of_a_kind", values[2])
#     elif isTwoPair:
#         return ("two_pair", values[3])
#     elif len(set(values)) == 4:
#         return ("one_pair", values[2])
#     else:
#         return ("high_card", values[4])
