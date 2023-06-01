from app.poker import *

g = Game()

# Add players
g.add_player("p1")
g.add_player("p2")
g.add_player("p3")
g.add_player("p4")


# Add players to seats
g.add_player_to_seat("p1", 100, 0) # dealer
g.add_player_to_seat("p2", 100, 1) # sb
g.add_player_to_seat("p3", 100, 2) # bb
g.add_player_to_seat("p4", 100, 3) # utg

print(g)

g.start_hand()
print(f"Dealer: {g.dealer_seat}")

g.fold("p4")
g.fold("p1")
g.fold("p2")


