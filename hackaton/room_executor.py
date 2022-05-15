import asyncio
from asyncio import Event

from .model.GameJson import Player, GameRules, Token, User, Message, MessageType
from fastapi import WebSocket
from typing import Dict, List, Optional

from .model.GameJson import User


class GameExecutor:
    def __init__(self, players):
        self.players = players

    async def run(self):
        print("Game run")

    async def await_for_end(self):
        print("Game awaiting for match")


class RoomExecutor:
    def __init__(self):
        self.host = None
        self.players: List[Player] = []
        self.task = Event()
        self.everyone_ready = Event()
        self.players_in_lobby = 0
        self.game = None
        self.rules = GameRules()
        self.next_player_id = 0

    async def run(self, websocket, name) -> Optional[GameExecutor]:
        self.host = Player(self.next_player_id, name, websocket, True, listening_task=None)
        self.next_player_id += 1
        self.players_in_lobby += 1
        self.players.append(self.host)
        while True:
            json: dict = await self.host.websocket.receive_json()
            if json.get("type"):
                if json.get("type")==MessageType.Quit:
                    print("host quits")
                    for player in self.players:
                        await player.websocket.send_json(Message(type=MessageType.Quit, message="quit").dict())
                    await self.host.websocket.close()
                    return None
                elif json.get("type")==MessageType.Start:
                    print("host starting")
                    self.players_in_lobby -= 1
                    for player in self.players:
                        await player.websocket.send_json(Message(type=MessageType.Start, message="start").dict())
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

    async def add_new_player(self, websocket, name):
        print(f"added new player {name}")
        player = Player(self.next_player_id, name, websocket, False, listening_task=None)
        self.next_player_id += 1
        self.players_in_lobby += 1
        player.listening_task = asyncio.create_task(self.listen_websocket(player))
        self.players.append(player)
        await player.websocket.send_json(self.rules.dict())
        await self.send_player_list()

    async def send_player_list(self):
        for player in self.players:
            await player.websocket.send_json(
                list(map(lambda x: User(id=x.id, name=x.name, is_host=x.is_host).dict(), self.players)))

    async def listen_websocket(self, player: Player):
        while True:
            json: dict = await player.websocket.receive_json()
            if json.get("type"):
                if json.get("type")==MessageType.Quit:
                    print(f"{player.name} quit")
                    await self.remove_player(player)
                elif json.get("type")==MessageType.Start:
                    print(f"{player.name} is ready")
                    self.players_in_lobby -= 1
                    if self.players_in_lobby == 0:
                        self.everyone_ready.set()
            else:
                pass

    async def remove_player(self, player):
        print("removed player")
        player.listening_task.cancel()
        if player.websocket is not None:
            await player.websocket.close()
        self.players.remove(player)
        await self.send_player_list()
        self.players_in_lobby -= 1

    async def start_game(self) -> GameExecutor:
        print("waiting for user start messages")
        await self.everyone_ready.wait()
        for player in self.players:
            if player.listening_task is not None:
                player.listening_task.cancel()
        self.game = GameExecutor(self.players)
        self.task.set()
        return self.game

    async def await_for_match(self) -> GameExecutor:
        """ let other websockets wait for match to be made """
        await self.task.wait()
        return self.game
