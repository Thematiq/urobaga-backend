import asyncio
from dataclasses import dataclass
from fastapi import WebSocket
from typing import Optional


class Token(BaseModel):
    token: str


class User(BaseModel):
    id: int
    name: str
    is_host: bool


@dataclass
class Player:
    id: int
    name: str
    websocket: WebSocket
    is_host: bool
    listening_task: Optional[asyncio.Task]


class GameRules(BaseModel):
    height: int = 10
    width: int = 5
    move_timeout: float = 30.0


class Starting(BaseModel):
    name: str
    starting: bool
