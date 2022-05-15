from fastapi import APIRouter, WebSocket, Depends, status
from typing import Optional, Dict

from starlette.websockets import WebSocketDisconnect

from .dependencies import get_name_and_room_token, get_match, get_quiz_game
from .model.GameJson import Token
from .room_executor import RoomExecutor
from .quiz import GameQuiz
import uuid

router = APIRouter(prefix='/ws')


@router.websocket('/match')
async def connect(
        websocket: WebSocket,
        name_token: Dict[str, Optional[str]] = Depends(get_name_and_room_token),
        db: Dict[str, RoomExecutor] = Depends(get_match),
        quiz: GameQuiz = Depends(get_quiz_game)):
    await websocket.accept()
    try:
        if name_token is None:
            await websocket.close(status.WS_1008_POLICY_VIOLATION)
            return
        name, token = name_token['name'], name_token['token']
        if token is None:
            await create_match(websocket, name, db, quiz)
        elif token in db:
            await join_match(websocket, name, db[token])
        else:
            await websocket.close(status.WS_1008_POLICY_VIOLATION)
    except WebSocketDisconnect:
        pass


async def create_match(
        websocket: WebSocket,
        name: str,
        db: Dict[str, RoomExecutor],
        quiz: GameQuiz):
    print('create new match')
    match = RoomExecutor(quiz)
    unique_token = uuid.uuid4().hex[:6].upper()
    while db.get(unique_token):
        unique_token = uuid.uuid4().hex[:6].upper()

    db[unique_token] = match
    await websocket.send_json(Token(token=unique_token).dict())
    game = await match.run(websocket, name)
    if game is None:
        return
    await game.run()


async def join_match(
        websocket: WebSocket,
        name: str,
        match: RoomExecutor):
    print('joining existing match')
    await match.add_new_player(websocket, name)
    game = await match.await_for_match()
    await game.await_for_end()
