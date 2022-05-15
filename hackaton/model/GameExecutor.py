import json
import multiprocessing
import random
import asyncio
import datetime

from pydantic import ValidationError

from .GameJson import PlayersOrder, Move, Message, ReplyModel, MessageType
from .player import Player
from typing import List


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

        while self.game_is_running:
            # Todo handle inactive users (and timeout for current user)
            # ... game_is_running = false
            asyncio.run(self.handle_inactive_users(self.rules.move_timeout))
            move = asyncio.run(self.handle_receive_move(self.rules.move_timeout))
            if move:
                # handle move
                if False:  # TODO !gameJudge.move(move):
                    error: Message(message="Invalid move!", type=MessageType.Error)
                    await self.players[self.player_id_with_move].websocket.send_json(error)
                    continue

                self.players_order.next_player()
                self.broadcast_move(move)    # Todo return move and fields
            else:
                # timeout
                self.players_order.next_player()
                self.broadcast_move(move, no_move=True)

    async def receive_move(self):
        try:
            # todo handle messages quit!!!!
            move = Move(await self.players[self.players_order.get_current_player_id()].websocket.receive_json())
            # self.handle_message_type(self.players_order.get_current_player_id())    # check if not quit
        except ValidationError as e:
            raise "JSON current player move error. " + str(e)
        return move

    async def handle_receive_move(self, timeout):
        try:
            move = await asyncio.wait_for(self.receive_move(), timeout=timeout)
        except asyncio.TimeoutError:
            move = False  # timeout
        return move

    def handle_message_type(self, message: Message, player_id):
        if message.type == MessageType.Quit:
            self.remove_player(player_id)

    def remove_player(self, player_id):
        # Todo
        print(f'Player {player_id} quit game.')
        # if len(player) < 2: self.is_running = false
        pass

    async def listen_for_exit_message(self, player):
        try:
            message = Message(await player.websocket.receive_json())
            if message.type == MessageType.Quit:
                self.remove_player(player.id)
        except ValidationError as e:
            raise "JSON player exit error." + str(e)

    async def handle_inactive_users(self, timeout):
        try:
            for player in self.players:
                if player.id != self.players_order.get_current_player_id():
                    await asyncio.wait_for(self.listen_for_exit_message(player), timeout=timeout)
        except asyncio.TimeoutError:
            pass  # timeout

    def broadcast_move(self, move, no_move=False):
        # Todo bez await
        await asyncio.wait([
            player.websocket.send_json(
                ReplyModel(
                    move=move,
                    player_order=self.get_players_order(player.id),
                    # field=
                    # questions=
                    no_move=no_move
                ))
            for player in self.players
        ])

    def get_players_order(self, player_id):
        players_list = []
        for i, player in enumerate(self.players_order.get_players_order()):
            players_list[i] = self.players_order.get_players_order()[player]

        can_move = player_id == self.players_order.get_current_player_id()
        player_order: PlayersOrder = PlayersOrder(order=players_list, can_move=can_move)
        return player_order


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
