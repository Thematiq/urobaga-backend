from fastapi import Cookie, Query, WebSocket
from typing import Optional, Dict, Tuple
from .mocks import MockMatchExecutor


magnificent_db = {}


async def get_name_and_room_token(
        _websocket: WebSocket,
        session: Optional[str] = Cookie(None),
        token: Optional[str] = Query(None),
        name: str = Query(None)) -> Tuple[str, Optional[str]]:
    if session is None and token is None:
        return None
    return (name, session or token)


async def get_match() -> Dict[str, MockMatchExecutor]:
    return magnificent_db

