import csv
import random

from model.quiz_question import QuizQuestion

def f(x):
    i, row = x
    q = QuizQuestion.parse_obj(row)
    q.id = i
    return q


class Quiz:
    def __init__(self):
        with open('quiz_questions/questions.csv') as csvfile:
            self.data = list(map(f, enumerate(csv.DictReader(csvfile))))
            self.data = dict(map(lambda x: (x.id, x), self.data))
            self.data = dict()
    def get_question(self, key):
        return self.data[key]


class GameQuiz:
    def __init__(self, quiz: Quiz):
        self.quiz = quiz
        self.available_questions = list(self.quiz.data.keys())

    def get_question(self):
        question_number = random.choice(self.available_questions)
        self.available_questions.remove(question_number)
        return self.quiz.get_question(question_number)



Quiz()