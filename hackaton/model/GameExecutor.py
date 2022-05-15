import asyncio
import random
from typing import List, Optional

from pydantic import ValidationError

from .GameJson import PlayersOrder, JsonMove, Message, ReplyModel, MessageType, Player, GameRules, BaseMessage, Point
from .quiz_question import QuizQuestion
from ..gamerules.gamejudge import GameJudge, GameRuleException
from ..quiz import GameQuiz


# Todo id for move
class GameExecutor:
    def __init__(self, players: List[Player], rules: GameRules, quiz: GameQuiz):
        self.task = asyncio.Event()
        self.quiz = quiz
        self.players = players
        self.players_order = PlayerOrder(players)
        self.rules = rules
        self.game_is_running = False
        self.gameJudge = GameJudge((rules.width, rules.height))

    async def send_initial_state(self):
        await asyncio.wait([
            player.websocket.send_json(self.get_players_order())
            for player in self.players
        ])
        self.game_is_running = True

    async def run(self):
        await self.send_initial_state()

        while self.game_is_running:
            move = await self.handle_receive_move(self.rules.move_timeout)
            if move:
                # handle move
                try:
                    questions = self.handle_move(move)
                except GameRuleException as e:
                    self.send_error(e.cause)
                    continue

                if questions:
                    # TODO handle questions
                    pass

                # wait for questions answeres
                field = self.confirm_move()

                move.user = self.players_order.get_current_player_id()
                self.players_order.next_player()
                self.broadcast_move(move, field)
            else:
                # timeout
                self.players_order.next_player()
                self.broadcast_move(move)
        self.task.set()

    # async def handle_questions(self, questions: List[QuizQuestion]) -> Optional[int]:
    #     answers = map(lambda x: x.correct_answer , questions)
    #     json_question = map()

    def confirm_move(self) -> List[Point]:
        player_id = -1
        # if questions correct then player else: id = -1
        move_field = self.gameJudge.apply_move(self.players_order.get_current_player_id())
        return move_field

    def handle_move(self, move: JsonMove) -> Optional[List[QuizQuestion]]:
        move_result_points = self.gameJudge.move(move.start_point, move.end_point)
        if move_result_points:
            return self.quiz.get_questions(move_result_points)
        return None

    async def send_error(self, message):
        error: Message = Message(message=message, type=MessageType.Error).dict()
        await self.players[self.players_order.get_current_player_id()].websocket.send_json(error)

    async def receive_move(self) -> Optional[JsonMove]:
        try:
            print(self.players_order.get_current_player_id())
            msg = BaseMessage.parse_obj(
                await self.players[self.players_order.get_current_player_id()].websocket.receive_json())

            if msg.type is MessageType.Quit:
                self.remove_player(self.players_order.get_current_player_id())
            elif msg.type is MessageType.Move:
                return msg
            else:
                raise "Current player message error"

        except ValidationError as e:
            raise "JSON current player move error. " + str(e)

    async def handle_receive_move(self, timeout) -> Optional[JsonMove]:
        try:
            return await asyncio.wait_for(self.receive_move(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

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

    async def broadcast_move(self, move, field: List[Point] = []):
        # Todo bez await
        print("move")
        await asyncio.wait([
            player.websocket.send_json(
                ReplyModel(
                    move=move,
                    player_order=self.get_players_order(),
                    field=field,
                ).dict())
            for player in self.players
        ])

    def get_players_order(self):
        players_list = []
        for i, player in enumerate(self.players_order.get_players_order()):
            players_list[i] = self.players_order.get_players_order()[player]

        player_order: PlayersOrder = PlayersOrder(
            order=players_list,
            current_player=self.players_order.get_current_player_id())
        return player_order

    async def await_for_end(self):
        await self.task.wait()


class PlayerOrder:
    def __init__(self, players):
        self.id = None
        self.players_order_list = self._chose_player_order(players)

    def _chose_player_order(self, players):
        self.id = 0
        players_order = list(range(len(players)))
        random.shuffle(players_order)
        print(f"shiffle: players_order")
        return players_order

    def get_players_order(self):
        return self.players_order_list

    def get_current_player_id(self) -> int:
        return self.players_order_list[self.id]

    def next_player(self):
        self.id += 1

