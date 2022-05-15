from fastapi import APIRouter, WebSocket, Depends, status
from typing import Optional, Dict

from starlette.websockets import WebSocketDisconnect

from .dependencies import get_name_and_room_token, get_match
from .model.GameJson import Token
from .room_executor import RoomExecutor
import uuid

router = APIRouter(prefix='/ws')


@router.websocket('/match')
async def connect(
        websocket: WebSocket,
        name_token: Dict[str, Optional[str]] = Depends(get_name_and_room_token),
        db: Dict[str, RoomExecutor] = Depends(get_match)):
    await websocket.accept()
    print("connect websocket")
    if name_token is None:
        await websocket.close(status.WS_1008_POLICY_VIOLATION)
        return
    name, token = name_token['name'], name_token['token']
    if token is None:
        await create_match(websocket, name, db)
    elif token in db:
        await join_match(websocket, name, db[token])
    else:
        await websocket.close(status.WS_1008_POLICY_VIOLATION)



async def create_match(
        websocket: WebSocket,
        name: str,
        db: Dict[str, RoomExecutor]):
    print('create new match')
    try:
        match = RoomExecutor()
        unique_token = uuid.uuid4().hex[:6].upper()
        while db.get(unique_token):
            unique_token = uuid.uuid4().hex[:6].upper()

        db[unique_token] = match
        await websocket.send_json(Token(token=unique_token).dict())
        game = await match.run(websocket, name)
        if game is None:
            return
        await game.run()
    except WebSocketDisconnect:
        await match.handle_host_quit()


async def join_match(
        websocket: WebSocket,
        name: str,
        match: RoomExecutor):
    print('joining existing match')
    try:
        player = await match.add_new_player(websocket, name)
        game = await match.await_for_match()
        await game.await_for_end()
    except WebSocketDisconnect:
        await match.handle_disconnect(player)
