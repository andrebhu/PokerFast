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
        self.current_action_seat = None
        self.last_action_seat = None
        self.community_cards = []
        self.current_bet = 0

        # Hand variables
        self.active_players = 0
        self.deck = Deck(_shuffle=True)
        self.dealer_seat = None
        self.pot = 0
        self.seats = [Seat() for _ in range(self.MAX_PLAYERS)]
        self.seats_cycle = cycle(self.seats)

        # Game variables
        self.blinds = blinds
        self.heads_up = False
        self.players = []
        self.state = "waiting"

    def __str__(self):
        s = ""
        s += f"State: {self.state}\n"
        s += f"Active players: {self.active_players}\n"

        s += f"Players:\n"
        for p in self.players:
            s += f"\t{p}\n"

        s += f"Seats:\n"
        for seat in self.seats:
            s += f"\t{seat}\n"

        s += f"Dealer: {self.dealer_seat}\n"
        s += f"Current action seat: {self.current_action_seat}\n"
        s += f"Last action seat: {self.last_action_seat}\n"
        s += f"Current bet: {self.current_bet}\n"
        s += f"Pot: {self.pot}\n"
        s += f"Community cards: {self.community_cards}\n"
        return s

    def get_player(self, username):
        """Helper function to get player"""
        for i in range(len(self.players)):
            if self.players[i].username == username:
                return self.players[i]

    def add_player(self, username):
        """Add a player to the game"""
        if self.get_player(username):
            raise Exception("Username already exists")

        p = Player(username)
        self.players.append(p)

    def shuffle_seats(self):
        """Shuffle the game's seats"""
        shuffle(self.seats)

    def add_player_to_seat(self, username, chips, i):
        """Add player to seat"""
        assert i < self.MAX_PLAYERS - 1, "Seat index out of range"

        p = self.get_player(username)
        if p:
            if self.seats[i].player == None:
                self.seats[i].player = p
                self.seats[i].chips = chips
                # self.active_players += 1
            else:
                raise Exception("Seat is taken")
        else:
            raise Exception("Player not found")
        

    def remove_player_from_seat(self, username):
        """Remove player from seat"""
        for seat in self.seats:
            if seat.player and seat.player.username == username:
                seat.player = None
                seat.chips = 0
                # self.active_players -= 1

    def get_next_active_seat(self):
        """Get the next active player that is not folded"""
        seat = next(self.seats_cycle)

        while seat.folded:
            seat = next(self.seats_cycle)

        return seat

    def pay(self, seat, amount):
        """Helper function to pay chips to pot"""
        if amount > seat.chips:
            # TODO: Handle all in and side pots
            raise Exception("Not enough chips")

        print(f"{seat.player.username} pays {amount} chips")
        seat.chips -= amount
        self.pot += amount

    # Controls the game's flow between rounds and player actions
    # Every player action should call update
    def update(self):
        """Update game state"""

        # TODO: Given last and current action seats, does this still need to be
        # checked? It also means the last person folded...?
        # End of hand because everyone else folded
        if self.active_players <= 1:
            winner_seat = self.get_next_active_seat()

            # Give winner the pot
            winner_seat.chips += self.pot
            self.pot = 0

            print("Everyone has folded!")
            print("Winner: ", winner_seat.player)

            self.end_hand()
            return
        

        # Checking end of round
        if self.current_action_seat == self.last_action_seat:
            print("Reached the end of the round!")
            if self.state == "preflop":
                print("Ending preflop, dealing flop...") # debugging
                self.current_bet = 0
                self.community_cards.append(self.deck.deal(3))
                self.state = "flop"

            elif self.state == "flop":
                print("Ending flop, dealing turn...") # debugging
                self.current_bet = 0
                self.community_cards.append(self.deck.deal(1))
                self.state = "turn"

            elif self.state == "turn":
                print("Ending turn, dealing river...") # debugging
                self.current_bet = 0
                self.community_cards.append(self.deck.deal(1))
                self.state = "river"

            elif self.state == "river":
                print("Ending river, showdown...") # debugging
                self.state = "showdown"
            return

        # Update action seat
        self.current_action_seat = self.get_next_active_seat()

    def start_hand(self):
        """Start round"""

        if self.state != "waiting":
            raise Exception("Round has already started, should not reach here")
        
        # Count active players
        self.active_players = 0
        for seat in self.seats:
            if seat.player:
                self.active_players += 1

        if self.active_players < 2:
            raise Exception("Not enough players")

        # Deal cards with a new deck
        self.deck = Deck(_shuffle=True)
        for seat in self.seats:
            if seat.player:
                seat.folded = False
                seat.cards = self.deck.deal(2)

        # Assign dealer as first active player
        self.dealer_seat = self.get_next_active_seat()

        # In a heads-up game, the dealer is the small blind and is first to act
        small_blind, big_blind = self.blinds[0], self.blinds[1]
        if self.active_players == 2:
            # Pay small blind
            self.pay(self.dealer_seat, small_blind)
            self.dealer_seat.last_bet = small_blind

            # Pay big blind
            temp_player = self.get_next_active_seat()
            self.pay(temp_player, big_blind)
            temp_player.last_bet = big_blind

            # TODO: Add logic if seat can't pay blinds
            self.current_bet = big_blind

            # Dealer is first to act
            self.current_action_seat = self.dealer_seat

            # Big blind is last to act
            self.last_action_seat = temp_player

        # In a game with more than two players, the player to the left of the
        # dealer is the small blind
        else:
            # Pay small blind
            self.current_action_seat = self.get_next_active_seat()
            self.pay(self.current_action_seat, small_blind)
            self.current_action_seat.last_bet = small_blind

            # Pay big blind
            self.current_action_seat = self.get_next_active_seat()
            self.pay(self.current_action_seat, big_blind)
            self.current_action_seat.last_bet = big_blind

            # TODO: Add logic if seat can't pay blinds
            self.current_bet = big_blind

            # Big blind is last to act
            self.last_action_seat = self.current_action_seat

            # Assign UTG as first to act
            self.current_action_seat = self.get_next_active_seat()

        self.state = "preflop"

    def end_hand(self):
        """End hand"""
        self.community_cards = []
        self.current_bet = 0
        self.pot = 0

        # Reset seats for next hand except for player and chips
        for seat in self.seats:
            seat.last_bet = 0
            seat.folded = True
            seat.cards = []

        # Recount active seated players
        self.active_players = 0
        for seat in self.seats:
            if seat.player:
                self.active_players += 1

        # Cleaning seats just incase
        self.current_action_seat = None
        self.last_action_seat = None

        # Cycle the cycler to the dealer so next hand moves the dealer position
        temp_player = next(self.seats_cycle)

        while temp_player != self.dealer_seat:
            temp_player = next(self.seats_cycle)

        self.state = "waiting"

    # Player actions
    def fold(self, username):
        """Fold"""
        if self.state not in ["preflop", "flop", "turn", "river"]:
            raise Exception("Game state is not valid")

        # Some type checking
        if isinstance(self.current_action_seat, Seat) and isinstance(
            self.current_action_seat.player, Player
        ):
            if self.current_action_seat.player.username != username:
                raise Exception("Not your turn!")
            else:
                print(f"{username} folds")  # debugging
                self.current_action_seat.folded = True
                self.active_players -= 1
                self.update()
        else:
            raise Exception("Something went wrong")

    def check(self, username):
        """Checking"""
        # If the current_bet is 0, then the player can check
        if self.state not in ["flop", "turn", "river"]:
            raise Exception("Game state is not valid")

        if isinstance(self.current_action_seat, Seat) and isinstance(
            self.current_action_seat.player, Player
        ):
            if self.current_action_seat.player.username != username:
                raise Exception("Not your turn!")
            else:
                print(f"{username} checks")  # debugging
                self.update()
        else:
            raise Exception("Something went wrong")

    def bet(self, username, amount):
        if self.state not in ["preflop", "flop", "turn", "river"]:
            raise Exception("Game state is not valid")

        if isinstance(self.current_action_seat, Seat) and isinstance(
            self.current_action_seat.player, Player
        ):
            if self.current_action_seat.player.username != username:
                raise Exception("Not your turn!")
            else:
                # TODO: Add all-in and side pot logic
                if amount > self.current_action_seat.chips:
                    raise Exception("Not enough chips")
                elif amount < self.current_bet * 2:
                    raise Exception("Bet must be two times greater than current bet")
                else:
                    print(f"{username} bets {amount} chips")  # debugging
                    self.pay(self.current_action_seat, amount)
                    self.current_action_seat.last_bet = amount
                    self.current_bet = amount
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
