from .model.player import Player


class RoomExecutor:
    def __init__(self):
        self.players: List[Player] = []

    def add_player(self, player):
        self.players.append(player)



