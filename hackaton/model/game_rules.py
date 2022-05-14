from pydantic import BaseModel


class GameRules(BaseModel):
    height: int = 20
    width: int = 20


