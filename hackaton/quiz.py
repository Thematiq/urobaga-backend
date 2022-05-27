import csv
import random
from os import path

from .model.quiz_question import QuizQuestion
from typing import List


def f(x):
    i, row = x
    q = QuizQuestion.parse_obj(row)
    q.id = i
    return q


class Quiz:
    def __init__(self):
        self.data = dict()
        with open(path.join(path.dirname(__file__), 'quiz_questions/questions.csv')) as csvfile:
            data = list(map(f, enumerate(csv.DictReader(csvfile))))
            self.difficulties = set()
            for row in data:
                self.difficulties.add(row.difficulty)
            self.difficulties = sorted(list(self.difficulties),reverse=True)
            for level in self.difficulties:
                self.data[level] = dict()

            for row in data:
                self.data[row.difficulty][row.id] = row



    def get_question(self, difficulty, key):
        return self.data[difficulty][key]


class GameQuiz:
    def __init__(self, quiz: Quiz):
        self.quiz = quiz
        self.available_questions = dict()
        for difficulty in self.quiz.difficulties:
            self.available_questions[difficulty] = list(self.quiz.data[difficulty].keys())

    def get_max_difficulty(self, points) -> int:
        for difficulty in self.quiz.difficulties:
            if difficulty > points:
                continue
            if len(self.available_questions[difficulty]) ==0:
                continue
            return difficulty

    def get_questions(self, points) -> List[QuizQuestion]:
        questions = []
        while points !=0:
            difficulty = self.get_max_difficulty(points)
            points -= difficulty
            question_number = random.choice(self.available_questions[difficulty])
            self.available_questions[difficulty].remove(question_number)
            questions.append(self.quiz.get_question(difficulty, question_number))

        return questions

