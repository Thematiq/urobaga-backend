from fastapi import Cookie, Query, WebSocket
from typing import Optional, Dict
from .mocks import MockMatchExecutor


magnificent_db = {}


async def get_room_token(
        _websocket: WebSocket,
        session: Optional[str] = Cookie(None),
        token: Optional[str] = Query(None)) -> Optional[str]:
    if session is None and token is None:
        return None
    return session or token


async def get_match() -> Dict[str, MockMatchExecutor]:
    return magnificent_db

