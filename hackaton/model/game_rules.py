from pydantic import BaseModel


class GameRules(BaseModel):
    height: int = 10
    width: int = 5


