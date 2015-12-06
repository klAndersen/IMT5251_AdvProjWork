"""
A simple Chat Agent with no intelligence that simply takes the presented
question and looks for an answer on StackOverflow. This is a simple
prototype, which is mostly preliminary work for my Master thesis which is
to create an Intelligent Chat Agent that can answer students questions
related to Programming by looking at posted answers on StackOverflow
(and potentially other sites within the StackExchange community).
"""


import pkg_resources

from xblock.core import XBlock
from xblock.fragment import Fragment
from xblock.fields import Scope, Dict

from answer import Answer
from mysqldatabase import MySQLDatabase
from searchstackexchange import SearchStackExchange


class ChatAgentXBlock(XBlock):
    """
    This class displays the Chat Agent to the user, and handles all
    the interactions, from retrieving the question/answer, to storing
    interactions into the database through the class ```MySQLDatabase```
    """

    __DEFAULT_SITE_TO_USE = "StackOverflow"
    """
    The default site to use if none other are specified.
    This is the only site that will be used in this project.
    """

    __ANSWER_TEXT_LENGTH = 150
    """
    The length of the returned answer displayed to the user.
    The length equals the number of characters before the
    text gets cut off with a 'Read more?'
    """

    user_dict = Dict(
        default={
            'user_id': 0,
            'username': 'default'
        },
        scope=Scope.content,
    )
    """
    This dictionary contains the user data related to the logged in user
    """

    retrieved_results_list = list()
    """
    This list contains all the search results that has been retrieved
    (currently not in use)
    """

    retrieved_answers_list = list()
    """
    This list contains all the answers that have been presented to the user
    """

    updated_answers_list = list()
    """
    This list contains all answers that have been updated
    (to avoid re-updating answers that have already been read)
    """

    def resource_string(self, path):
        """
        Handy helper for getting resources from our kit.

        Arguments:
            path

        """
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view which displays the Chat Agent to the students.

        Arguments:
            context
        """
        html = self.resource_string("static/html/chatagent.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/chatagent.css"))
        frag.add_javascript(self.resource_string("static/js/src/chatagent.js"))
        frag.initialize_js('ChatAgentXBlock')
        return frag

    @XBlock.json_handler
    def get_default_welcome_message(self, data, suffix=''):
        """
        Get the default welcome message that the user is presented with upon entering the chat.

        Arguments:
            data (dict): JSON dictionary containing the username {'username': username}
            suffix (str):

        Returns:
             JSON: The retrieved welcome message; {'welcome_msg': welcome_msg}

        """
        # TODO 1: In the master thesis, either retrieve this from DB, or just use this one
        # TODO 2: Add question to welcome message
        welcome_msg = "Welcome, "
        # check that username is set
        if data['username'] is not None:
            welcome_msg += "<i>" + data['username'] + "</i>."
        welcome_msg += "<br />I see that you came from a page with the following Question: <br />"
        welcome_msg += "<i>&lt;question_displayed_here&gt;</i>"  # TODO 2: insert question here
        welcome_msg += "<br /> Is this the question you are looking for? Please enter 'Yes' or 'No'."
        welcome_msg += "<p><br /></p>"
        return {'welcome_msg': welcome_msg}

    @XBlock.json_handler
    def get_username(self, data, suffix=''):
        """
        Get the name of the currently logged in/active user to display his/her name in the chat agent.

        Arguments:
            data (dict): JSON dictionary
            suffix (str):

        Returns:
             JSON: The retrieved username; {'username': username}

        """
        # Perhaps move this to student_view function
        default = "default"
        if len(self.user_dict) == 0 or self.user_dict.get('username') == default:
            # TODO: Retrieve (and/or) store the username of the currently active/logged in user
            # self.xmodule_runtime.anonymous_student_id => this isn't there anymore it seems
            username = default
            # store username, and add name to welcome message
            user_id = self.__store_username_in_database(default)
            self.user_dict = {
                'user_id': user_id,
                'username': username
            }
        username = self.user_dict.get('username')
        return {'username': username}

    @XBlock.json_handler
    def handle_user_input(self, data, suffix=''):
        """
        Function for processing user input to retrieve answer from StackOverflow

        Arguments:
            data (dict): JSON dictionary containing users input {'user_input': user_input}
            suffix (str):

        Returns:
             dict:
             |  results_dict = {
             |         'title': title,
             |         'response': response,
             |         'read_more': read_more,
             |     }

        """
        # get and set relevant data
        title = ""
        read_more = ""
        asked_by_user = True
        contains_html = False
        edx_question_id = None
        use_adv_search = False
        user_input = data['user_input']
        user_id = self.user_dict.get('user_id')
        selected_site = self.__DEFAULT_SITE_TO_USE
        try:
            # store question and retrieve its id
            question_id = self.__store_question_in_database(user_id, user_input, asked_by_user, edx_question_id)
            search_stackexchange = SearchStackExchange(selected_site)
            # was the search executed successfully?
            results_found = search_stackexchange.process_search_results_for_question(user_input, use_adv_search)
            if results_found:
                # test question: 'Py-StackExchange filter by tag'
                res_list = search_stackexchange.get_list_of_results()
                if len(res_list) == 1:
                    res_obj = res_list[0]
                else:
                    # TODO: handle multiple results here... for now, just retrieve the first one
                    res_obj = res_list[0]

                # just retrieve the first result - this will be updated in master thesis version
                answer_list = search_stackexchange.get_question_data(0)
                if len(answer_list) > 0:
                    contains_html = True
                    answer_body = self.__retrieve_answer(True, answer_list, res_obj.get_link(), question_id)
                else:
                    answer_body = "No answers were found for this question."
                # display result to user
                answer_index = len(self.retrieved_answers_list) - 1
                title = "<i>" + res_obj.get_title() + "</i><p /><div id='answer_body' " \
                                                      "class='answer_body' data-index='" + str(answer_index) + "'>"
                response = answer_body[:self.__ANSWER_TEXT_LENGTH]
                read_more = ("</div>"
                             "<div id='read_more' id='read_more'>"
                             "<strong style='cursor: pointer' id='read_more_text' "
                             "class='read_more_text'>Read more?</strong>"
                             "<input id='answer_index' class='answer_index' name='answer_index'"
                             "value='" + str(answer_index) + "' type='hidden'></div>"
                             if len(answer_body) > self.__ANSWER_TEXT_LENGTH else "")
            else:
                response = "No results matching this question."
        except AttributeError, err:
            response = "An error occurred during processing. The error is: " + str(err)
        # set values in dictionary
        results_dict = {
            'title': title,
            'response': response,
            'read_more': read_more,
            'contains_html': contains_html
        }
        return results_dict

    @XBlock.json_handler
    def show_or_hide_answer_text(self, data, suffix=''):
        """
        Some answers may have a long text to them, which means
        they are not always shown full text. This function takes
        the current view mode, and either returns the full text
        or the partial text for display.

        Arguments:
            data (dict): JSON dictionary containing answer index
                and whether answer should be hidden or shown
            suffix (str):

        Returns:
             dict:
             |  results_dict = {
             |  'index': index,
             |  'response': response
             |  }

        """
        response = ''
        index = int(data['index'])
        read_more = data['read_more']
        answer_list = self.retrieved_answers_list
        # is the index valid?
        if len(answer_list) > index > -1:
            answer = answer_list[index]
            # which version of answer should be displayed?
            if read_more:
                response = answer.get_answer_text()
                if len(answer_list) > index > -1:
                    answer = answer_list[index]
                    update_dict = {
                        'answer_id': answer.get_answer_id(),
                        # 'answer_text': answer.get_answer_text(),
                        # 'question_id': answer.get_question_id(),
                        'is_answer_read': True,
                        # 'correct_answer': 0,
                        # 'stackexchange_id': answer.get_stackexchange_id(),
                    }
                    self.__update_answer_in_database(False, "is_answer_read", update_dict)
            else:
                response = answer.get_answer_text()[:self.__ANSWER_TEXT_LENGTH]
        results_dict = {
            'index': index,
            'response': response
        }
        return results_dict

    def __retrieve_answer(self, select_accepted_answer=bool, answer_list=list(), link=str, question_id=long):
        """
        This function retrieves from the passed list the Answer that either is marked as accepted answer
        (if it exists and ```select_accepted_answer``` is True). If not, the most highest voted answer
        is returned. If only one answer exists, this is returned without any checks.

        Arguments:
            select_accepted_answer (bool): If it exists, should the answer marked as accepted be returned?
            answer_list (list): The list of answer objects based on JSONModel from stackexchange
            link (str): The link to the StackExchange site where this questions exists
            question_id (long): The MySQL database ID for the Question

        See:
            |  ```stackexchange.Answers```

        Returns:
            str: The HTML body of the selected answer

        """
        answer_body = None
        if len(answer_list) > 1:
            highest_vote = -1
            index_of_highest_voted = -1
            index_of_accepted_answer = -1
            # loop through answers and check for highest voted and accepted answer
            for index in range(0, len(answer_list)):
                if answer_list[index].is_accepted:
                    index_of_accepted_answer = index
                if answer_list[index].score > highest_vote:
                    highest_vote = answer_list[index].score
                    index_of_highest_voted = index
            # which answer should be retrieved?
            if select_accepted_answer and index_of_accepted_answer > -1:
                answer_body = answer_list[index_of_accepted_answer].body
            else:
                answer_body = answer_list[index_of_highest_voted].body
        elif len(answer_list) == 1:
            # only one answer, retrieve it
            answer_body = answer_list[0].body
        # log this answer in the database
        self.__store_answer_in_database(answer_body, link, question_id, False)
        return answer_body

    @staticmethod
    def __store_username_in_database(username=str):
        """
        Stores the currently asked question in the database.

        Arguments:
            username (str): The name of the currently active user

        Returns:
            long: The primary key of this user in the MySQL database

        """
        user_dict = {
            'username': username
        }
        pk_user = MySQLDatabase().insert_into_table_chat_users(user_dict)
        return pk_user

    @staticmethod
    def __store_question_in_database(user_id=int, question=str, asked_by_user=bool, edx_question_id=None):
        """
        Stores the currently asked question in the database.

        Arguments:
            question (str): The question that was asked
            asked_by_user(bool): Is this a question phrased by user, or taken from Open Edx course?
            user_id (int): User ID of the user asking the chatbot this question
            edx_question_id (int): The EDX ID of the question (if this was taken from an EDX course)

        Returns:
            long: The primary key of the inserted question

        """
        question_dict = {
            'question_text': question,
            'asked_by_user': asked_by_user,
            'user_id': user_id,
            'edx_question_id': edx_question_id
        }
        pk_question = MySQLDatabase().insert_into_table_questions(question_dict)
        return pk_question

    def __store_answer_in_database(self, answer=str, se_link=str, question_id=long, is_answer_read=bool, correct_answer=bool):
        """
        Stores the currently presented answer in the database.

        Arguments:
            answer (str): The answer text that was retrieved and presented
            se_link (str): The link (url) to the site where answer was retrieved from
            question_id (long): The ID for the question that was asked (primary key in MySQL db)
            is_answer_read (bool): Has the read more option been clicked?
            correct_answer (bool): Is this answer accepted by the chat agent user as the correct one?

        """
        # temp dictionary for database insertion
        answer_dict = {
            'answer_text': answer,
            'stackexchange_link': se_link,
            'question_id': question_id,
            'is_answer_read': is_answer_read,
            'correct_answer': correct_answer
        }
        answer_dict = MySQLDatabase().insert_into_table_answers(answer_dict)
        answer_id = answer_dict.get("answer_id")
        stackexchange_id = answer_dict.get("stackexchange_id")
        answer = Answer(answer_id, answer, question_id, is_answer_read, correct_answer, stackexchange_id, se_link)
        self.retrieved_answers_list.append(answer)

    def __update_answer_in_database(self, update_all=bool, update_key=str, update_dict=dict):
        """
        Updates the data for the answer with the passed ID.

        Arguments:
            update_all (bool): Update all values for this answer
            update_key (str) (None): Key for value to update (if single value)
            update_dict (dict): Value(s) to update

        Returns:
             bool: True if data was updated, False otherwise.

        """
        index = 0
        not_found = True
        updated = False
        answer_id = update_dict.get("answer_id")
        # check if the given answer already has been updated
        while not_found and index < len(self.updated_answers_list):
            if answer_id == self.updated_answers_list[index]:
                not_found = False
            index += 1
        if not_found:
            index = -1
            max_size = len(self.retrieved_answers_list) - 1
            # if the answer hasn't been updated, does it exist?
            while not_found and index <= max_size:
                answer = self.retrieved_answers_list[index]
                index += 1
                if answer.get_answer_id() == answer_id:
                    not_found = False
            if not_found is False:
                if update_key is not None and not self.__does_key_match_answer_dictionary(update_key):
                    raise ValueError("The given key does not match the existing key set.")
                updated = MySQLDatabase().update_tbl_answers(update_key, update_dict, update_all)
            if updated:
                self.__update_answer_list(index, update_all, update_key, update_dict)
        return updated

    def __update_answer_list(self, index=int, update_all=bool, update_key=None, update_dict=dict):
        """
        Updates the object data in the list based on the values in the ```update_dict```.
        For now, this function only updates for all entries, not singular values.

        Arguments:
            index (int): The index of the Answer object to update
            update_all (bool): Should all attributes be updated?
            update_key (str) (None): If only one value was updated, pass the key to that value in ```update_dict```
            update_dict (dict): Dictionary containing the values that were changed

        """
        if update_all:
            orig_answer = self.retrieved_answers_list[index]
            answer_id = orig_answer.get_answer_id()
            answer_text = update_dict.get("answer_text")
            is_answer_read = update_dict.get("is_answer_read")
            correct_answer = update_dict.get("correct_answer")
            question_id = update_dict.get("question_id")
            stackexchange_id = update_dict.get("stackexchange_id")
            stackexchange_link = orig_answer.get_stackexchange_link()
            updated_answer = Answer(answer_id, answer_text, question_id, is_answer_read, correct_answer,
                                    stackexchange_id, stackexchange_link)
            self.retrieved_answers_list[index] = updated_answer
            self.updated_answers_list.append(answer_id)
        else:
            orig_answer = self.retrieved_answers_list[index]
            answer_id = orig_answer.get_answer_id()
            answer_text = orig_answer.get_answer_text()
            is_answer_read = update_dict.get("is_answer_read")
            correct_answer = orig_answer.get_is_correct_answer()
            question_id = orig_answer.get_question_id()
            stackexchange_id = orig_answer.get_stackexchange_id()
            stackexchange_link = orig_answer.get_stackexchange_link()
            updated_answer = Answer(answer_id, answer_text, question_id, is_answer_read, correct_answer,
                                    stackexchange_id, stackexchange_link)
            self.retrieved_answers_list[index] = updated_answer
            self.updated_answers_list.append(answer_id)

    @staticmethod
    def __does_key_match_answer_dictionary(update_key=str):
        """
        Check if the passed key matches the expected values in the answer dictionary

        Arguments:
            update_key (str) (None): The key for the value to update

        Returns:
            bool: True if key exists, false otherwise
        """
        # dummy dictionary with dummy data - just to confirm that key is valid
        answer_dictionary = {
            'answer_id': 0,
            'answer_text': "dummy",
            'question_id': 0,
            'is_answer_read': 0,
            'correct_answer': 0,
            'stackexchange_id': 0,
        }
        if update_key in answer_dictionary:
            return True
        return False

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("Chat Agent",
             """<vertical_demo>
                <chatagent/>
                </vertical_demo>
             """),
        ]
