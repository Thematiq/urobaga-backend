from asyncio import Event
from fastapi import WebSocket
from typing import List


class MockGameExecutor:
    def __init__(self, players: List[WebSocket]):
        self.sockets = players
        self.task = Event()

    async def run(self) -> None:
        while True:
            pass

    async def await_for_end(self) -> None:
        await self.task.wait()


class MockMatchExecutor:
    def __init__(self):
        self.sockets = []
        self.task = Event()
        self.game = None

    async def run(self, websocket: WebSocket) -> MockGameExecutor:
        while True:
            break
        return await self.start_game()

    async def add_new_player(self, websocket: WebSocket) -> None:
        self.sockets.append(websocket)

    async def start_game(self) -> MockGameExecutor:
        self.game = MockGameExecutor(self.sockets)
        self.task.set()
        return self.game

    async def await_for_match(self) -> MockGameExecutor:
        """ let other websockets wait for match to be made """
        await self.task.wait()
        return self.game
