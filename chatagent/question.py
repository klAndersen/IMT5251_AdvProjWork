_author_ = "Knut Lucas Andersen"


class Question:

    __question_id = None
    __question_text = None
    __edx_question_id = None
    __created_by_user_id = None
    __question_list = {}

    def __init__(self, question_id, question_text, edx_qustion_id, created_by_user_id):
        self.__question_id = question_id
        self.__question_text = question_text
        self.__edx_question_id = edx_qustion_id
        self.__created_by_user_id = created_by_user_id

    def find_question_by_id(self, question_id):
        raise NotImplementedError

    def find_edx_question_by_id(self, edx_id):
        raise NotImplementedError

    def get_question_id(self):
        return self.__question_id

    def get_question_text(self):
        return self.__question_text

    def get_question_edx_id(self):
        return self.__edx_question_id

    def get_question_user_id(self):
        return self.__created_by_user_id

