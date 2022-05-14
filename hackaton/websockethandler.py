from fastapi import APIRouter, WebSocket, Depends, status
from typing import Optional, Dict

from .dependencies import get_name_and_room_token, get_match
from .room_executor import RoomExecutor

router = APIRouter(prefix='/ws')


@router.websocket('/match')
async def connect(
        websocket: WebSocket,
        name_token: Optional[str] = Depends(get_name_and_room_token),
        db: Dict[str, MockMatchExecutor] = Depends(get_match)):

    name, token = name_token[0], name_token[1]
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
    match = RoomExecutor()
    db['randomString'] = match
    game = await match.run(websocket, name)
    await game.run()


async def join_match(
        websocket: WebSocket,
        name: str,
        match: RoomExecutor):
    print('joining existing match')
    await match.add_new_player(websocket, name)
    game = await match.await_for_match()
    await game.await_for_end()
