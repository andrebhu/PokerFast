from app.poker import *

g = Game()

# Add players
g.add_player("bobby")
g.add_player("jimmy")
g.add_player("steve")
g.add_player("joe")
g.add_player("albert")
g.add_player("eddie")
g.add_player("bryan")
g.add_player("james")
g.add_player("pizza")

# Add players to seats
g.add_player_to_seat("bobby", 1000, 0)
g.add_player_to_seat("jimmy", 1000, 1)
g.add_player_to_seat("steve", 1000, 2)
g.add_player_to_seat("bryan", 1000, 3)

# g.shuffle_seats()
g.start_round()
