import asyncio
from asyncio import Event
from typing import List, Optional

from .model.GameExecutor import GameExecutor
from .model.GameJson import Player, GameRules, MessageType, PlayerList, User, Quit, Start, Token
from .quiz import GameQuiz


class RoomExecutor:
    def __init__(self, quiz: GameQuiz, token):
        self.token = token
        self.quiz = quiz
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
        await self.host.websocket.send_json(Token(token=self.token, user_id=self.host.id).dict())
        await self.send_player_list()
        await self.host.websocket.send_json(self.rules.dict())
        while True:
            print("host waiting for messages")
            json: dict = await self.host.websocket.receive_json()
            print(json.get("type"))
            if json.get("type") == MessageType.Quit.value:
                print("host quits")
                for player in self.players:
                    await player.websocket.send_json(Quit().dict())
                await self.host.websocket.close()
                return None
            elif json.get("type") == MessageType.Start.value:
                print("host starting")
                self.players_in_lobby -= 1
                for player in self.players:
                    await player.websocket.send_json(Start().dict())
                break
            elif json.get('type') == MessageType.Rules.value:
                print("host rules")
                try:
                    self.rules = GameRules.parse_obj(json)
                except Exception:
                    continue
                for player in self.players:
                    await player.websocket.send_json(self.rules.dict())
            else:
                print("sth else")
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
        await player.websocket.send_json(Token(token=self.token, user_id=player.id).dict())
        await self.send_player_list()
        await player.websocket.send_json(self.rules.dict())
        return player

    async def handle_disconnect(self, player):
        player.listening_task.cancel()
        if player.websocket is not None:
            await player.websocket.close()
        self.players.remove(player)
        await self.send_player_list()
        self.players_in_lobby -= 1

    async def handle_host_quit(self):
        self.players.remove(self.host)
        for player in self.players:
            await player.websocket.send_json(Quit().dict())
        if self.host.websocket is not  None:
            await self.host.websocket.close()

    async def send_player_list(self):
        for player in self.players:
            await player.websocket.send_json(
                PlayerList(players=list(
                    map(lambda x: User(id=x.id, name=x.name, is_host=x.is_host).dict(), self.players))).dict())

    async def listen_websocket(self, player: Player):
        while True:
            json: dict = await player.websocket.receive_json()
            if json.get("type"):
                if json.get("type") == MessageType.Quit.value:
                    print(f"{player.name} quit")
                    await self.remove_player(player)
                elif json.get("type") == MessageType.Start.value:
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
        self.game = GameExecutor(self.players, self.rules, self.quiz)
        self.task.set()
        return self.game

    async def await_for_match(self) -> GameExecutor:
        """ let other websockets wait for match to be made """
        await self.task.wait()
        return self.game
