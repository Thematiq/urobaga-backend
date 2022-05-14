from pydantic import BaseModel


class GameRules(BaseModel):
    height: int
    width: int


