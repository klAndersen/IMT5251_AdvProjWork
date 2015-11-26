"""
A simple Chat Agent with no intelligence that simply takes the presented question
and looks for an answer on StackOverflow. This is a simple prototype, which is mostly
preliminary work for my Master thesis which is to create an Intelligent Chat Agent that
can answer students questions related to Programming by looking at posted answers on
StackOverflow (and potentially other sites within the StackExchange community).
"""

import pkg_resources
import stackexchange

from xblock.core import XBlock
from xblock.fragment import Fragment
from xblock.fields import Scope, Dict, List

from mysqldatabase import MySQLDatabase
from searchstackexchange import SearchStackExchange


class ChatAgentXBlock(XBlock):
    """
    This class displays the Chat Agent to the user, and handles all
    the interactions, from retrieving the question/answer, to storing
    interactions into the database through the class ```MySQLDatabase```
    """

    __STACK_EXCHANGE_CLIENT_ID = 6041
    """
    Client ID for StackExchange API, see: https://api.stackexchange.com/docs/authentication
    """

    __STACK_EXCHANGE_KEY = "DMercir86DS8ZhXwHZ)vxg(("
    """
    Key for StackExchange API, see: https://api.stackexchange.com/docs/authentication
    """

    # contains the active users data
    user_dict = Dict(
        default={
            'user_id': 0,
            'username': 'default'
        },
        scope=Scope.content,
    )

    # contains all the search results
    retrieved_results_dict = List(
        default=[],
        scope=Scope.content,
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view which displays the Chat Agent to the students.
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
            data
            suffix (str)

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
            data
            suffix (str)

        Returns:
             JSON: The retrieved username; {'username': username}

        """
        # Perhaps move this to student_view function
        default = "default"
        if len(self.user_dict) == 0 or self.user_dict.get('username') == default:
            # TODO: Retrieve (and/or) store the username of the currently active/logged in user
            username = default  # self.xmodule_runtime.anonymous_student_id # this isn't there anymore it seems
            # store username, and add name to welcome message
            user_id = self.store_username_in_database(default)
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
            data
            suffix (str)

        Returns:
             JSON: The loaded content; {'result': result}

        """
        # get and set relevant data
        user_id = self.user_dict.get('user_id')
        user_input = data['user_input']
        asked_by_user = True
        edx_question_id = None
        result = ""
        try:
            # store the question, and retrieve its id
            question_id = self.store_question_in_database(user_id, user_input, asked_by_user, edx_question_id)
            # retrieve data from StackOverflow
            selected_site = stackexchange.Site(stackexchange.StackOverflow, self.__STACK_EXCHANGE_KEY)
            # TODO: Turn off debugging options
            stackexchange.impose_throttling = True
            stackexchange.throttle_stop = False
            stackexchange.web.WebRequestManager.debug = True
            search_stackexchange = SearchStackExchange()
            # was the search executed successfully?
            search_result = search_stackexchange.process_search_results_for_question(selected_site, user_input)
            if type(search_result) is bool and search_result is False:
                result = "No results found matching asked question."
            else:
                # test question: 'Py-StackExchange filter by tag'
                res_list = search_stackexchange.get_list_of_results()
                if len(res_list) == 1:
                    res_obj = res_list[0]
                else:
                    # TODO: handle multiple results here... for now, just retrieve the first one
                    res_obj = res_list[0]
                # TODO: Use data to retrieve and add answer to chatbot (lookup needed; for now link is returned)
                result = "<a class='link' id='link' target='_blank' href='" \
                         + res_obj.get_link() + "'>" + res_obj.get_link() + "</a>"
        except Exception, ex:
            result += "An error occurred during processing. The error is: " + str(ex)
        return {'result': result}

    @staticmethod
    def store_username_in_database(username=str):
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
    def store_question_in_database(user_id=int, question=str, asked_by_user=bool, edx_question_id=None):
        """
        Stores the currently asked question in the database.

        Arguments:
            question (str): The question that was asked
            asked_by_user(bool): Is this a question phrased by user, or taken from Open Edx course?
            user_id (int): User ID of the user asking the chatbot this question
            edx_question_id (int): The EDX ID of the question (if this was taken from an EDX course)

        Returns:
            long: The primary key of the inserted data

        """
        question_dict = {
            'question_text': question,
            'asked_by_user': asked_by_user,
            'user_id': user_id,
            'edx_question_id': edx_question_id
        }
        pk_question = MySQLDatabase().insert_into_table_questions(question_dict)
        return pk_question

    @staticmethod
    def store_answer_in_database(answer=str, so_link=str, question_id=int, correct_answer=bool):
        """
        Stores the currently presented answer in the database.

        Arguments:
            answer (str): The answer text that was retrieved and presented
            so_link (str): The link (url) to the site where answer was retrieved from
            question_id (int): The ID for the question that was asked (primary key in MySQL db)
            correct_answer (bool): Is this answer accepted by the chat agent user as the correct one?

        Returns:
            bool: True if data was saved, False otherwise

        """
        answer_dict = {
            'answer_text': answer,
            'stackoverflow_link': so_link,
            'question_id': question_id,
            'correct_answer': correct_answer
        }
        stored = MySQLDatabase().insert_into_table_answers(answer_dict)
        return stored

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
