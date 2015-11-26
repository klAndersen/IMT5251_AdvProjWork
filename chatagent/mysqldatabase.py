
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
    # Constant values: Error values
    PRIMARY_KEY_NOT_FOUND = -1
    # "Constant" values: Table names
    __TBL_ANSWERS = "tblChatAnswers"
    __TBL_CHAT_USERS = "tblChatUsers"
    __TBL_USER_FEEDBACK = "tblUserFeedback"
    __TBL_STACKOVERFLOW = "tblStackOverflow"
    __TBL_QUESTIONS = "tblChatQuestions"
    __TBL_FEEDBACK_QUESTIONS = "tblFeedbackQuestions"
    # "Constant" values: Primary keys
    __PK_USERS = "chatUserID"
    __PK_QUESTIONS = "chatQuestionID"
    __PK_ANSWERS = "chatAnswersID"
    __PK_STACKOVERFLOW = "stackoverflowID"

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
            self.__db.autocommit(True)
        except MySQLdb.Error as err:
            print("Error during connection: %s", err)

    def get_all_question_and_answer_records(self, where=None, where_args=dict):
        """
        Retrieves all questions and answers from the database

        Arguments:
            where (str):
                |  (Optional) The WHERE clause string (use ```%(where_args_key)s``` for values).
                |  E.g: 'WHERE username = %(username)s',
                |  and where_args = {'username': 'lucas'}
            where_args (dict): (Requires ```where```) Dictionary with values for the where clause

        See:
            | ```MySQLCursor.fetchall()```
            | ```MySQLdb.cursors.DictCursor```

        Returns:
            dict: Dictionary containing the result of the query || None

        """
        result_set = None
        try:
            query = "SELECT *  FROM " \
                    + self.__TBL_ANSWERS + ", " \
                    + self.__TBL_QUESTIONS + ", " \
                    + self.__TBL_STACKOVERFLOW
            # if there is a WHERE clause, add it
            if where is not None:
                query += " " + where
            query += ";"
            cursor = self.__get_db_cursor()
            # execute query based on whether or not there is a WHERE clause
            if where is not None:
                cursor.execute(query, where_args)
            else:
                cursor.execute(query)
            result_set = cursor.fetchall()
        except MySQLdb.Error as err:
            print("MySQLdb.Error (Retrieve QA): %s", err)
        finally:
            self.__close_db_connection()
        return result_set

    def insert_into_table_chat_users(self, user_dictionary=dict):
        """
        Checks if user is stored in database, if not the username is stored in the MySQL database.

        Arguments:
            user_dict (dict):
                |  The name of the current user of the application.
                |  Expects key to be ```username```.

        Returns:
            long: The primary key of the inserted data || ```PRIMARY_KEY_NOT_FOUND```

        """
        # check if user exists to avoid duplicate insertion
        pk_user = self.__check_if_user_exists(user_dictionary)
        if pk_user > self.PRIMARY_KEY_NOT_FOUND:
            return pk_user
        # user doesn't exists, store user in database
        query = "INSERT INTO " + self.__TBL_CHAT_USERS + " VALUES (" \
                + "null, " \
                + "%(username)s" \
                + ");"
        try:
            cursor = self.__get_db_cursor()
            cursor.execute(query, user_dictionary)
            pk_user = cursor.lastrowid
        except MySQLdb.Error as err:
            print("MySQLdb.Error: %s", err)
        finally:
            self.__close_db_connection()
        return pk_user

    def insert_into_table_questions(self, question_dictionary=dict):
        """
        Stores the Question data in the MySQL database

        Arguments:
            question_dictionary (dict):
                |  Expects a dictionary containing the following keys/values:
                |  - edx_question_id (int): ID of question in EDX
                |    (if question is from e.g. course test) || None
                |  - question_text (str): The question that was asked
                |  - asked_by_user (bool): Is this question asked/phrased by the user?
                |  - user_id (int): The user ID of the user interacting with the application

        Returns:
            long: The primary key of the inserted question || ```PRIMARY_KEY_NOT_FOUND```

        """
        pk_question = self.__check_if_question_exists(question_dictionary)
        if pk_question > self.PRIMARY_KEY_NOT_FOUND:
            return pk_question
        query = "INSERT INTO " + self.__TBL_QUESTIONS + " VALUES (" \
                + "null, " \
                + "%(edx_question_id)s, " \
                + "%(question_text)s, " \
                + "%(asked_by_user)s, " \
                + "%(user_id)s " \
                + ");"
        try:
            cursor = self.__get_db_cursor()
            cursor.execute(query, question_dictionary)
            pk_question = cursor.lastrowid
        except MySQLdb.Error as err:
            print("MySQLdb.Error (INS Q): %s", err)
        finally:
            self.__close_db_connection()
        return pk_question

    def insert_into_table_answers(self, answer_dictionary=dict):
        """
        Stores the Answer data and Stack* link in the MySQL database

        Arguments:
            answer_dictionary (dict):
                |  Expects a dictionary containing the following keys/values:
                |  - answer_text (str): The answer that was found
                |  - correct_answer (bool): Value for whether or not this answer was accepted by the user
                |  - question_id (int): The (MySQL) Question ID of the question that was asked
                |  - stackoverflow_link (str): The link (URL) to the page where the answer was retrieved from

        Returns:
            bool:
            |  True: Data was saved.
            |  False: Data was not saved

        """
        data_saved = False
        query = "INSERT INTO " + self.__TBL_ANSWERS + " VALUES (" \
                + "null, " \
                + "%(answer_text)s, " \
                + "%(correct_answer)s, " \
                + "%(stackoverflow_id)s, " \
                + "%(question_id)s " \
                + ");"
        try:
            cursor = self.__get_db_cursor()
            # insert (or retrieve) the link and get its primary key
            temp_dict = {'stackoverflow_link': answer_dictionary.get('stackoverflow_link')}
            stackoverflow_id = self.__insert_into_table_stackoverflow(temp_dict)
            # was a primary key returned?
            if stackoverflow_id == self.PRIMARY_KEY_NOT_FOUND:
                return data_saved
            # update the dictionary by removing the link, and adding the stackoverflow id
            answer_dictionary.pop('stackoverflow_link', None)
            answer_dictionary.update({'stackoverflow_id': stackoverflow_id})
            cursor.execute(query, answer_dictionary)
            data_saved = True
        except MySQLdb.Error as err:
            print("MySQLdb.Error (INS ANS): %s", err)
        finally:
            self.__close_db_connection()
        return data_saved

    def insert_into_table_user_feedback(self, user_feedback_dictionary=dict):
        """
        Stores the user feedback in the MySQL database

        Arguments:
            user_feedback_dictionary (dict):
                        |  Expects a dictionary containing the following keys/values:
                        |  - feedback_text (str): The feedback that was given
                        |  - feedback_type_id (int): The type of feedback that was given
                        |  (e.g. which form/question was filled out?)
                        |  - user_id (int): The user ID of the user interacting with the application

        Returns:
            bool:
            |  True: Data was saved.
            |  False: Data was not saved

        """
        data_saved = False
        query = "INSERT INTO " + self.__TBL_USER_FEEDBACK + " VALUES (" \
                + "null, " \
                + "%(feedback_text)s, " \
                + "%(feedback_type_id)s, " \
                + "%(user_id)s " \
                + ");"
        try:
            cursor = self.__get_db_cursor()
            cursor.execute(query, user_feedback_dictionary)
            data_saved = True
        except MySQLdb.Error as err:
            print("MySQLdb.Error: %s", err)
        finally:
            self.__close_db_connection()
        return data_saved

    def __select_all_records_from_tables(self, table_list):
        """
        Retrieves all records from the selected tables.

        This function takes a list as input, where you can add one or more table names
        to retrieve all the data from. The passed list is converted to a tuple for
        string interpolation. Therefore, user data should not be passed to this function,
        since table names cannot be parameterized (it is neither the intention that this
        function should be called/used through user input).

        Arguments:
            table_list (list): List containing the names of tables to retrieve data from

        See:
            | ```MySQLCursor.fetchall()```
            | ```MySQLdb.cursors.DictCursor```

        Returns:
            dict: Dictionary containing the result of the query || None

        """
        result_set = None
        try:
            cursor = self.__get_db_cursor()
            query = "SELECT * FROM %s"
            no_of_entries = len(table_list) - 1
            # if there are more then one table in the list...
            if no_of_entries > 0:
                for counter in range(0, no_of_entries):
                    query += ", %s"
            # add semi-colon to end query string
            query += ";"
            # run query and get the results
            cursor.execute(query % tuple(table_list))
            result_set = cursor.fetchall()
        except MySQLdb.Error as err:
            print("MySQLdb.Error (Select all): %s", err)
        finally:
            self.__close_db_connection()
        return result_set

    def __insert_into_table_stackoverflow(self, stackoverflow_dictionary=dict):
        """
        Stores the link to StackOverflow where the answer(s) was retrieved from in the MySQL database.
        Note! This function does not close the database connection.

        Arguments:
            stackoverflow_dictionary (dict):
                    |  Expects a dictionary containing the following keys/values:
                    |  - stackoverflow_link (str): The link (URL) to the page where the answer was retrieved from

        Returns:
            long: The primary key of the inserted link

        """
        pk_stackoverflow = self.__check_if_stackoverflow_link_exists(stackoverflow_dictionary)
        if pk_stackoverflow > self.PRIMARY_KEY_NOT_FOUND:
            return pk_stackoverflow
        query = "INSERT INTO " + self.__TBL_STACKOVERFLOW + " VALUES (" \
                + "null, " \
                + "%(stackoverflow_link)s, " \
                + "NOW()" \
                + ");"
        try:
            cursor = self.__get_db_cursor()
            cursor.execute(query, stackoverflow_dictionary)
            pk_stackoverflow = cursor.lastrowid
        except MySQLdb.Error as err:
            print("MySQLdb.Error (INS SO): %s", err)
        return pk_stackoverflow

    def __check_if_user_exists(self, user_dictionary=dict):
        """
        Checks if a user with given username is already registered in the database.

        Arguments:
            user_dict (dict):
                |  The name of the current user of the application.
                |  Expects key to be ```username```.

        Returns:
            long: Primary key || ```PRIMARY_KEY_NOT_FOUND```

        """
        try:
            pk_name = self.__PK_USERS
            table_name = self.__TBL_CHAT_USERS
            where = "WHERE username = %(username)s"
            where_args = {'username': user_dictionary.get('username')}
            primary_key = self.__get_primary_key_of_table(pk_name, table_name, where, where_args)
            if primary_key > self.PRIMARY_KEY_NOT_FOUND:
                return primary_key
        except ValueError as err:
            print("Error: %s", err)
        return self.PRIMARY_KEY_NOT_FOUND

    def __check_if_question_exists(self, question_dictionary=dict):
        """
        Checks if the given question is already registered in the database.

        Arguments:
            question_dictionary (dict):
                |  Expects a dictionary containing the following keys/values:
                |  - edx_question_id (int): ID of question in EDX
                |    (if question is from e.g. course test) || None
                |  - question_text (str): The question that was asked
                |  - asked_by_user (bool): Is this question asked/phrased by the user?
                |  - user_id (int): The user ID of the user interacting with the application

        Returns:
            long: Primary key || ```PRIMARY_KEY_NOT_FOUND```

        """
        try:
            pk_name = self.__PK_QUESTIONS
            table_name = self.__TBL_QUESTIONS
            where = "WHERE question_text = %(question_text)s"
            where_args = {'question_text': question_dictionary.get('question_text')}
            question_id = self.__get_primary_key_of_table(pk_name, table_name, where, where_args)
            if question_id > self.PRIMARY_KEY_NOT_FOUND:
                return question_id
        except ValueError as err:
            print("Error: %s", err)
        except MySQLdb.Error as err:
            print("MySQLdb.Error (SO_ID): %s", err)
        return self.PRIMARY_KEY_NOT_FOUND

    def __check_if_stackoverflow_link_exists(self, stackoverflow_dictionary=dict):
        """
        Checks if the given link is already registered in the database.

        Arguments:
            stackoverflow_dictionary (dict):
                |  The link to the relevant stackoverflow page.
                |  Expects key to be ```stackoverflow_link```.

        Returns:
            long: Primary key || ```PRIMARY_KEY_NOT_FOUND```

        """
        try:
            pk_name = self.__PK_STACKOVERFLOW
            table_name = self.__TBL_STACKOVERFLOW
            where = "WHERE stackoverflow_link = %(stackoverflow_link)s"
            where_args = {'stackoverflow_link': stackoverflow_dictionary.get('stackoverflow_link')}
            stackoverflow_id = self.__get_primary_key_of_table(pk_name, table_name, where, where_args)
            if stackoverflow_id > self.PRIMARY_KEY_NOT_FOUND:
                return stackoverflow_id
        except ValueError as err:
            print("Error: %s", err)
        except MySQLdb.Error as err:
            print("MySQLdb.Error (SO_ID): %s", err)
        return self.PRIMARY_KEY_NOT_FOUND

    def __get_primary_key_of_table(self, pk_name=str, table_name=str, where=str, where_args=dict):
        """
        Retrieves the primary key of the given entry in the given table

        Arguments:
            pk_name (str): The name of the primary key to retrieve
            table_name (str): The table to retrieve the primary key from
            where (str):
                | The WHERE clause string (use ```%(where_args_key)s``` for values).
                |  E.g: 'WHERE username = %(username)s',
                |  and where_args = {'username': 'lucas'}
            where_args (dict): Dictionary with values for the where clause

        See:
            | ```MySQLCursor.fetchall()```
            | ```MySQLdb.cursors.DictCursor```

        Throws:
            ValueError: Throws exception if any of the passed values are empty (None)

        Returns:
            long: Primary key based on passed WHERE statement || ```PRIMARY_KEY_NOT_FOUND```

        """
        error_msg = None
        if pk_name is None:
            error_msg = "Primary key name cannot be empty!"
        elif table_name is None:
            error_msg = "Table name cannot be empty!"
        elif where is None or not where_args:
            error_msg = "Where clause and where arguments cannot be empty!"
        # was there any errors?
        if error_msg is not None:
            raise ValueError(error_msg)
        # everything okay, attempt to retrieve and return primary key
        primary_key = self.PRIMARY_KEY_NOT_FOUND
        try:
            query = "SELECT " + pk_name + " FROM " + table_name + " " + where + ";"
            cursor = self.__get_db_cursor()
            cursor.execute(query, where_args)
            result_set = cursor.fetchone()
            if result_set is None:
                return self.PRIMARY_KEY_NOT_FOUND
            primary_key = result_set[pk_name]
        except MySQLdb.Error as err:
            print("MySQLdb.Error (GET PK): %s", err)
        return primary_key

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
        try:
            self.__db.cursor(MySQLdb.cursors.DictCursor).close()
            self.__db.close()
        except MySQLdb.ProgrammingError as err:
            # if the error is that the connection is already closed, ignore it
            if str(err) == "closing a closed connection":
                pass
            else:
                print("MySQLdb.ProgrammingError: %s", err)
        except MySQLdb.Error as err:
            print("MySQLdb.Error (Close Connection): %s", err)

