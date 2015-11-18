"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources

from xblock.core import XBlock
# from xblock.fields import Scope, Integer
from xblock.fragment import Fragment

import stackexchange

# from mysqldatabase import MySQLDatabase


class ChatAgentXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the ChatAgentXBlock, shown to students
        when viewing courses.
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
    def print_test_data(self, data, suffix=''):
        """
        Just a dummy function to print random content.
        Examples are:
        - Data from MySQL
        - Data from StackOverflow
        - ...

        Arguments:
            data
            suffix (str)

        Returns:
             JSON: The loaded content; {'result': result}

        """
        # return {'result': MySQLDatabase().print_table_content()}
        so = stackexchange.Site(stackexchange.StackOverflow)
        my_favourite_guy = so.user(41981)
        result = my_favourite_guy.reputation.format()
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
