
import MySQLdb

import dbconfig as config

_author_ = "Knut Lucas Andersen"


class MySQLDB:
    """
    Class for handling MySQL database operations.
    The main goal of this class is to save test data from user experiments.
    """

    __db = None  # the database connection
    __mysql_parameters = None  # parameters for database connection

    def __init__(self):
        """
        Constructor connecting to the MySQL database.
        """
        self.__mysql_parameters = config.mysql_parameters
        self.__db = MySQLdb.connect(
            self.__mysql_parameters['host'],
            self.__mysql_parameters['user'],
            self.__mysql_parameters['passwd'],
            self.__mysql_parameters['db']
        )

    def __get_db_cursor(self):
        """
        Returns a cursor for executing database operations.

        See:
            ```MySQLdb.cursors.DictCursor```

        Returns:
            MySQLdb.connect.cursor

        """
        return self.__db.cursor(MySQLdb.cursors.DictCursor)

    def print_table_content(self, table_name):
        """
        Dummy function for testing that db connection works and that content is retrieved.
        Will most likely be removed or re-named later on.

        Arguments
            table_name (str): The name of the table to retrieve content from

        """
        # executes the given SQL query
        query = "SELECT * FROM " + table_name + ";"
        cursor = self.__get_db_cursor()
        cursor.execute(query)
        result_set = cursor.fetchall()

        for row in result_set:
            print "%s, %s" % (row["userID"], row["firstName"])


tbl_name = "tblUser"
MySQLDB().print_table_content(tbl_name)
