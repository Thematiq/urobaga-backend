import json
import multiprocessing
import random
import asyncio
import datetime

from .GameJson import PlayersOrder, Move, ErrorMsg, ReplyModel
from .player import Player
from typing import List


class PlayerOrder:
    def __init__(self, players):
        self.id = None
        self.players_order_list = self._chose_player_order(players)

    def _chose_player_order(self, players):
        self.id = 0
        players_order = list(range(len(players)))
        random.shuffle(players_order)
        return players_order

    def get_players_order(self):
        return self.players_order_list

    def get_current_player_id(self):
        return self.players_order_list[self.id]

    def next_player(self):
        self.id += 1


class GameExecutor:
    def __init__(self, players: List[Player], rules):
        self.players = players
        self.players_order = PlayerOrder(players)
        self.rules = rules
        self.game_is_running = False
        # self.gameJudge = GameJudge()

    async def run(self):
        # initial msg with players order
        await asyncio.wait([
            player.websocket.send_json(self.get_players_order(player.id))
            for player in self.players
        ])

        self.game_is_running = True

        # Todo handle inactive users or timeout
        # ... game_is_running = false

        while self.game_is_running:
            move = asyncio.run(handle_receive_move())
            if move:
                # handle move
                if False:  # TODO !gameJudge.move(move):
                    error: ErrorMsg(message="Invalid move!")
                    await self.players[self.player_id_with_move].websocket.send_json(error)
                    continue

                broadcast_move(move)
                self.players_order.next_player()
            else:
                # timeout
                self.players_order.next_player()
                broadcast_move(move, no_move=True)

    def handle_move_receiver(self):
        p = multiprocessing.Process(target=self.receive_move(), name="MoveReceiver")
        p.start()

    async def receive_move(self):
        try:
            move = Move(await self.players[self.players_order.get_current_player_id()].websocket.receive_json())
        except json.JSONDecoder:  # TODO?
            raise "JSON current player move error."
        return move

    async def handle_receive_move(self):
        try:
            move = await asyncio.wait_for(self.receive_move(), timeout=10.0)
        except asyncio.TimeoutError:
            move = False    # timeout

        return move

    def broadcast_move(self, move, no_move=False):
        # Todo bez await
        await asyncio.wait([
            player.websocket.send_json(
                ReplyModel(
                    move=move,
                    player_order=self.players_order.get_players_order(),
                    no_move=no_move))
            for player in self.players
        ])

    def get_players_order(self, player_id):
        players_list = []
        for i, player in enumerate(self.players_order.get_players_order()):
            players_list[i] = self.players_order.get_players_order()[player]

        can_move = player_id == self.players_order.get_current_player_id()
        player_order: PlayersOrder = PlayersOrder(order=players_list, can_move=can_move)
        return player_order
