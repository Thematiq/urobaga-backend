from dataclasses import dataclass
from fastapi import WebSocket
from typing import Optional


@dataclass
class Player:
    name: str
    websocket: WebSocket
    is_host: Optional[bool]

