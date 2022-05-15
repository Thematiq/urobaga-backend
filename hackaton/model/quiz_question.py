from typing import List, Optional

from pydantic import BaseModel


class QuizQuestion(BaseModel):
    id: Optional[int]
    question: str
    difficulty: int
    answer_0: str
    answer_1: str
    answer_2: str
    answer_3: str
    correct_answer: Optional[int]

    def __hash__(self):
        return hash((self.id))