import csv
from model.quiz_question import QuizQuestion


class Quiz:
    def __init__(self):
        with open('quiz_questions/questions.csv') as csvfile:
            self.data = set(map(lambda x: QuizQuestion.parse_obj(x), csv.DictReader(csvfile)))
            print(self.data)





Quiz()