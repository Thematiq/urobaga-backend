import asyncio
from asyncio import Event

from .model.player import Player
from .model.game_rules import GameRules
from .model.exit import Exit
from .model.starting import Starting
from fastapi import WebSocket
from typing import Dict, List, Optional

from .model.user import User


class GameExecutor:
    def __init__(self,players):
        self.players = players

    async def run(self):
        print("Game run")

    async def await_for_match(self):
        print("Game awaiting for match")

class RoomExecutor:
    def __init__(self):
        self.host = None
        self.players: List[Player] = []
        self.task = Event()
        self.game = None
        self.rules = GameRules()
        self.next_player_id = 0 # moze lepiej

    async def run(self, websocket, name) -> Optional[GameExecutor]:
        self.host = Player(self.next_player_id, name, websocket, True, False, listening_task=None)
        self.next_player_id += 1
        self.players.append(self.host)
        while True:
            json: dict = await self.host.websocket.receive_json()
            if json.get("exit"):
                print("host exit")
                for player in self.players:
                    await player.websocket.send_json(Exit(exit=True).dict())
                await self.host.websocket.close()
                return None
            elif json.get("starting"):
                print("host starting")
                self.host.ready_to_play = True
                for player in self.players:
                    await player.websocket.send_json(Starting(name=player.name, starting=True).dict())
                while not self.is_everyone_ready():
                    continue
                break
            elif json.get('height'):
                print("host rules")
                try:
                    self.rules = GameRules.parse_obj(json)
                except Exception:
                    continue
                for player in self.players:
                    await player.websocket.send_json(self.rules.dict())

            else:
                pass

        print("starting game")
        return await self.start_game()

    def is_everyone_ready(self):
        for player in self.players:
            if not player.ready_to_play:
                return False
        return True

    async def add_new_player(self, websocket, name):
        print(f"added new player {name}")
        player = Player(self.next_player_id, name, websocket, False, False, listening_task=None)
        self.next_player_id += 1
        player.listening_task = asyncio.create_task(self.listen_websocket(player))
        self.players.append(player)
        await self.send_player_list()

    async def send_player_list(self):
        for player in self.players:
            await player.websocket.send_json(list(map(lambda x: User(id=x.id, name=x.name, is_host=x.is_host).dict(), self.players)))

    async def listen_websocket(self, player: Player):
        while True:
            json: dict = await player.websocket.receive_json()
            if json.get("exit"):
                print(f"{player.name} exited")
                await self.remove_player(player)
            elif json.get("starting"):
                print(f"{player.name} is ready")
                player.ready_to_play = True
            else:
                pass

    async def remove_player(self, player):
        print("removed player")
        player.listening_task.cancel()
        await player.websocket.close()
        self.players.remove(player)
        await self.send_player_list()


    async def start_game(self) -> GameExecutor:
        self.game = GameExecutor(self.players)
        self.task.set()
        return self.game

    async def await_for_match(self) -> GameExecutor:
        """ let other websockets wait for match to be made """
        await self.task.wait()
        return self.game



