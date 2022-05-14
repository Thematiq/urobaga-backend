from pydantic import BaseModel


class Starting(BaseModel):
    name: str
    starting: bool

    

