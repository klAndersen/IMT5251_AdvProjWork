_author_ = "Knut Lucas Andersen"

# TODO: Consider merging this and QuestionClass, to use these as objects for storing user input


class Answer:

    __answer_id = None
    __answer_text = None
    __question_id = None
    __stackoverflow_id = None
    __stackoverflow_link = None

    def __init__(self, answer_id, answer_text, question_id, stackoverflow_id, stackoverflow_link):
        self.__answer_id = answer_id
        self.__answer_text = answer_text
        self.__question_id = question_id
        self.__stackoverflow_id = stackoverflow_id
        self.__stackoverflow_link = stackoverflow_link

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

