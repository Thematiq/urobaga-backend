from fastapi import Cookie, Query, WebSocket
from typing import Optional, Dict, Tuple
from .mocks import MockMatchExecutor
from .quiz import Quiz, GameQuiz


magnificent_db = {}

quiz = Quiz()


async def get_quiz_game():
    return GameQuiz(quiz)


async def get_name_and_room_token(
        _websocket: WebSocket,
        session: Optional[str] = Cookie(None),
        token: Optional[str] = Query(None),
        name: str = Query(None)) -> Dict[str, Optional[str]]:
    return {"name": name, "token": session or token if session or token else None}


async def get_match() -> Dict[str, MockMatchExecutor]:
    return magnificent_db

