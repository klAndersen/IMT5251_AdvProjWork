"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources

from xblock.core import XBlock
# from xblock.fields import Scope, Integer
from xblock.fragment import Fragment

import stackexchange

from mysqldb import MySQLDatabase


class ChatAgentXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

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
    def print_test_data(self, data, suffix=''):
        """
        Just a dummy function to print random content.
        Examples are:
        - Data from MySQL
        - Data from StackOverflow
        - ...

        Returns:
             JSON: The loaded content
        """
        # tbl_name = "tblChatUsers"
        # return {'result': MySQLDatabase().print_table_content(tbl_name)}
        so = stackexchange.Site(stackexchange.StackOverflow)
        my_favourite_guy = so.user(41981)
        result = my_favourite_guy.reputation.format()
        # result = "hello"
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
