from typing import Iterable

from ask.questions import Question


class QuestionSet:
    def __init__(self, questions: Iterable[Question]):
        self.questions = questions

    def ask(self):
        ans = {}

        for question in self.questions:
            ans[question.name] = question.ask()

        return ans
