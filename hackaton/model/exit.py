from typing import Optional

from pydantic import BaseModel


class Exit(BaseModel):
    exit: bool


