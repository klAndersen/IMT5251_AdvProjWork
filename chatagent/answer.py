_author_ = "Knut Lucas Andersen"


class Answer:

    __answer_id = None
    __answer_text = None
    __question_id = None
    __stackoverflow_id = None
    __stackoverflow_link = None

    def __init__(self):
        raise NotImplementedError

    def get_answer_id(self):
        return self.__answer_id

    def get_answer_text(self):
        return self.__answer_text

    def get_question_id(self):
        return self.__question_id

    def get_stackoverflow_id(self):
        return self.__stackoverflow_id

    def get_stackoverflow_link(self):
        return self.__stackoverflow_link

