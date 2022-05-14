import asyncio
from .model.player import Player
from .model.game_rules import GameRules
from .model.exit import Exit
from .model.starting import Starting
from fastapi import  WebSocket
from typing import Dict

class GameExecutor:
    pass


class RoomExecutor:
    def __init__(self):
        self.host = None
        self.players: List[Player] = []
        self.task = Event()
        self.game = None
        self.rules = GameRules()
        self.next_player_id = 0 # moze lepiej

    async def run(self, websocket, name) -> GameExecutor:
        self.host = Player(self.next_player_id, name, websocket, True, False, listening_task=None)
        self.players.append(host)
        self.next_player_id += 1
        while True:
            json: dict = await host.websocket.receive_json()
            if json.get("exit"):
                for player in self.players:
                    player.websocket.send(Exit(exit=True))
            elif json.get("starting"):
                self.host.ready_to_play = True
                for player in self.players:
                    player.websocket.send(Starting(starting=True))
                while not self.is_everyone_ready():
                    continue
                break
            elif json.get('height'):
                try:
                    self.rules = GameRules.parse_obj(json)
                except Exception:
                    pass
            else:
                pass

        return await self.start_game()

    def is_everyone_ready(self):
        for player in self.players:
            if not player.ready_to_play:
                return False
        return True

    async def add_new_player(self, websocket, name):
        player = Player(self.next_player_id, name, websocket, False, False, listening_task=None)
        self.next_player_id += 1
        player.listening_task = asyncio.create_task(self.listen_websocket(player))
        self.players.append(player)

    async def listen_websocket(self, player: Player):
        while True:
            json: dict = await player.websocket.receive_json()
            if json.get("exit"):
                self.remove_player(player)
            elif json.get("starting"):
                player.ready_to_play = True
            else:
                pass


    async def remove_player(self, player):
        player.listening_task.cancel()
        player.websocket.close()
        self.players.remove(player)


    async def start_game(self) -> GameExecutor:
        self.game = GameExecutor(self.players)
        self.task.set()
        return self.game

    async def await_for_match(self) -> GameExecutor:
        """ let other websockets wait for match to be made """
        await self.task.wait()
        return self.game



