import asyncio
from dataclasses import dataclass
from fastapi import WebSocket
from typing import Optional


@dataclass
class Player:
    id: int
    name: str
    websocket: WebSocket
    is_host: bool
    ready_to_play: bool
    listening_task: Optional[asyncio.Task]
