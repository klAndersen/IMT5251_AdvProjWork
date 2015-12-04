_author_ = "Knut Lucas Andersen"

# TODO: Consider merging this and QuestionClass, to use these as objects for storing user input


class Answer:

    __answer_id = None
    __answer_text = None
    __question_id = None
    __is_answer_read = None
    __is_correct_answer = None
    __stackexchange_id = None
    __stackexchange_link = None

    def __init__(self, answer_id=long, answer_text=str, question_id=long, is_answer_read=bool, is_correct_answer=bool,
                 stackexchange_id=long, stackexchange_link=str):
        """
        Constructor for the Answer class

        Arguments:
            answer_id (long): The ID for this answer
            answer_text (str): The answer
            question_id (long): The ID for the question to which this answer belongs
            is_answer_read (bool): Is this answer read?
            is_correct_answer (bool): Is this answer marked as correct?
            stackexchange_id (long): The ID of the StackExchange site which this answer is retrieved from
            stackexchange_link (str): The link to the StackExchange site which this answer is retrieved from

        """
        self.__answer_id = answer_id
        self.__answer_text = answer_text
        self.__question_id = question_id
        self.__is_answer_read = is_answer_read
        self.__is_correct_answer = is_correct_answer
        self.__stackexchange_id = stackexchange_id
        self.__stackexchange_link = stackexchange_link

    def get_answer_id(self):
        return self.__answer_id

    def get_answer_text(self):
        return self.__answer_text

    def get_is_answer_read(self):
        return self.__is_answer_read

    def get_is_correct_answer(self):
        return self.__is_correct_answer

    def get_question_id(self):
        return self.__question_id

    def get_stackexchange_id(self):
        return self.__stackexchange_id

    def get_stackexchange_link(self):
        return self.__stackexchange_link

