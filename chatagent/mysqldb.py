
import MySQLdb

import dbconfig as config

_author_ = "Knut Lucas Andersen"


class MySQLDatabase:
    """
    Class for handling MySQL database operations.
    The main goal of this class is to save test data from user experiments.
    """

    __db = None  # the database connection
    __mysql_parameters = None  # parameters for database connection
    # "Constant" values: Table names
    __TBL_ANSWERS = "tblChatAnswers"
    __TBL_CHAT_USERS = "tblChatUsers"
    __TBL_USER_FEEDBACK = "tblUserFeedback"
    __TBL_STACKOVERFLOW = "tblStackOverflow"
    __TBL_CHAT_QUESTIONS = "tblChatQuestions"
    __TBL_FEEDBACK_QUESTIONS = "tblFeedbackQuestions"

    def __init__(self):
        """
        Constructor connecting to the MySQL database.
        """
        try:
            # retrieve connection parameters from config file
            self.__mysql_parameters = config.mysql_parameters
            # attempt to connect to the database
            self.__db = MySQLdb.connect(
                self.__mysql_parameters['host'],
                self.__mysql_parameters['user'],
                self.__mysql_parameters['passwd'],
                self.__mysql_parameters['db']
            )
        except MySQLdb.Error as err:
            print(err)

    def __get_db_cursor(self):
        """
        Returns a cursor for executing database operations.

        See:
            ```MySQLdb.cursors.DictCursor```

        Returns:
            MySQLdb.connect.cursor

        """
        return self.__db.cursor(MySQLdb.cursors.DictCursor)

    def __close_db_connection(self):
        """
        Closes the cursor and the connection to the database
        """
        self.__db.cursor(MySQLdb.cursors.DictCursor).close()
        self.__db.close()

    def __execute_query(self, query):
        """
        Runs a query against the database and returns the cursor containing the result

        Arguments:
            query (str): The query to run against the database

        Returns:
            MySQLdb.connect.cursor: The result of the executed query

        """
        cursor = self.__get_db_cursor()
        cursor.execute(query)
        return cursor

    def print_table_content(self, table_name):
        """
        Dummy function for testing that db connection works and that content is retrieved.
        Will most likely be removed or re-named later on.

        Arguments:
            table_name (str): The name of the table to retrieve content from

        Returns:
            str: The result of the db query
            
        """
        content = ""
        # executes the given SQL query
        query = "SELECT * FROM " + table_name + ";"
        cursor = self.__execute_query(query)
        result_set = cursor.fetchall()

        for row in result_set:
            content += "%s, %s" % (row["chatUserID"], row["username"])
            content += "\n"
        self.__close_db_connection()
        content += "\n-End-"
        return content
