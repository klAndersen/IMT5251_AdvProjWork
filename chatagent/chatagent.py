"""
A simple Chat Agent with no intelligence that simply takes the presented question
and looks for an answer on StackOverflow. This is a simple prototype, which is mostly
preliminary work for my Master thesis which is to create an Intelligent Chat Agent that
can answer students questions related to Programming by looking at posted answers on
StackOverflow (and potentially other sites within the StackExchange community).
"""

import pkg_resources
from  stackexchange import *

from xblock.core import XBlock
# from xblock.fields import Scope, Integer
from xblock.fragment import Fragment


# from mysqldatabase import MySQLDatabase
from searchstackexchange import *


class ChatAgentXBlock(XBlock):
    """
    This class displays the Chat Agent to the user, and handles all
    the interactions, from retrieving the question/answer, to storing
    interactions into the database through the class ```MySQLDatabase```
    """

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
        username = "default"
        # TODO: Retrieve the username of the currently active/logged in user
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
        user_input = data['user_input']

        selected_site = Site(StackOverflow)
        # debugging options
        StackExchange.impose_throttling = True
        StackExchange.throttle_stop = False
        StackExchange.web.WebRequestManager.debug = True
        search_stackexchange = SearchStackExchange()

        # test question: 'Py-StackExchange filter by tag'
        search_stackexchange.process_search_results_for_question(selected_site, user_input)
        res_list = search_stackexchange.get_list_of_results()
        res_obj = None
        if len(res_list) == 1:
            res_obj = res_list[0]
        else:
            # TODO: handle multiple results here... for now, just retrieve the first one
            res_obj = res_list[0]
        # TODO: Use data to retrieve and add answer to chatbot (lookup needed)
        result = "<a class='link' id='link' target='_blank' href='" \
                 + res_obj.get_link() + "'>" + res_obj.get_link() + "</a>"

        return {'result': result}

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
