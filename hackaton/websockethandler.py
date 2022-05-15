from fastapi import APIRouter, WebSocket, Depends, status
from typing import Optional, Dict

from .dependencies import get_room_token, get_match
from .mocks import MockMatchExecutor

router = APIRouter(prefix='/ws')


@router.websocket('/match')
async def connect(
        websocket: WebSocket,
        token: Optional[str] = Depends(get_room_token),
        db: Dict[str, MockMatchExecutor] = Depends(get_match)):
    if token is None:
        await create_match(websocket, db)
    elif token in db:
        await join_match(websocket, db[token])
    else:
        await websocket.close(status.WS_1008_POLICY_VIOLATION)


async def create_match(
        websocket: WebSocket,
        db: Dict[str, MockMatchExecutor]):
    print('create new match')
    match = MockMatchExecutor()
    db['randomString'] = match
    game = await match.run(websocket)
    await game.run()


async def join_match(
        websocket: WebSocket,
        match: MockMatchExecutor):
    print('joining existing match')
    await match.add_new_player(websocket)
    game = await match.await_for_match()
    await game.await_for_end()
