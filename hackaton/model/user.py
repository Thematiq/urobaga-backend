from pydantic import BaseModel
from fastapi import WebSocket
from typing import Optional


class User(BaseModel):
    name: str
    websocket: WebSocket
    is_host: Optional[bool]

