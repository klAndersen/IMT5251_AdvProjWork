import json
import stackexchange

"""
This file contains all classes that are used to objectify, handle and process search results.
It can be debated whether or not creating my own objects is a good idea, since the Py-StackExchange
comes with its own models, see: https://github.com/lucjon/Py-StackExchange/blob/master/stackexchange/models.py

The problem with this however, is that the format returns the Question model, which leads to me not being able
to retrieve the currently accepted answer (presuming there is one). For this project, I think the code will be
as-is, but this may be updated and changed during my Master thesis.

As for the comment marked '# noinspection PyUnresolvedReferences', this is used to disable warning from PyCharm.
"""

_author_ = "Knut Lucas Andersen"


class SearchStackExchange:
    """
    Class for searching and returning results from StackExchange by using the py-stackexchange API.

    The main goal of this class is to handle search, lookup answers and all other required interactions
    with the StackExchange community
    """

    __PAGE_SIZE = 100
    """
    The amount of pages returned can be very large depending on search parameters and search used.
    Regardless, it is doubtful that more than 100 pages will contain the answer, and if so the
    user should re-phrase the question to get more consistent results
    """

    __STACK_EXCHANGE_CLIENT_ID = 6041
    """
    Client ID for StackExchange API, see: https://api.stackexchange.com/docs/authentication
    """

    __STACK_EXCHANGE_KEY = "DMercir86DS8ZhXwHZ)vxg(("
    """
    Key for StackExchange API, see: https://api.stackexchange.com/docs/authentication
    """

    NO_KEY_VALUE_FOR_ENTRY = -1
    """
    Constant for values that were not found, or was not set when retrieving the search results
    """

    __site = None

    def __init__(self, site_name=str):
        """
        Constructor for the class searching the given StackExchange site for information.
        Throws error if site is not found

        Arguments:
            site_name (str): Name of the StackExchange community site to use.
                Please note that the name is case-sensitive

        """
        self.__result_list = list()
        # use debugging
        self.__use_debugging()
        self.__site = self.__convert_user_input_to_stackexchange_site(site_name)

    def process_search_results_for_question(self, question=str, use_adv_search=bool):
        """
        Runs a search against the set StackExchange site, looking for questions that
        matches the content of ```question```. There are two options for the search,
        ```search``` and ```search_advanced```. The executed search is selected from
        the passed value ```use_adv_search```. The function returns either True or False
        depending on whether or not the search executed successfully, and if any results
        were found. The results are stored in a list, which can be retrieved by calling
        ```get_list_of_results```.

        Note! ```search_advanced``` can easily return several thousands of hits just
        because one of the words in a given page matches question. Use this with
        caution.

        Arguments:
            question (str): The question to search for
            use_adv_search (bool): Should ```search_advanced``` be used?

        See:
            |  ```stackexchange.Site.search```
            |  ```stackexchange.Site.search_advanced```

        Returns:
            bool: ```False```: search had no results (or failed).
            ```True```: search was successful.

        """
        search = None
        site = self.__site
        # execute the selected search
        if use_adv_search:
            # Note! This returns basically everything without any filtering
            # Therefore, ensure that the result has at least one answer
            search = site.search_advanced(q=question, answers=1)
        else:
            search = site.search(intitle=question, pagesize=self.__PAGE_SIZE)
        # was a result returned?
        if (search is None) or (len(search.items) == 0):
            return False

        # Note! If a large result set is returned, it may go through the first result page twice
        # I'm not sure why this happens, but it only happens for the first result page, and only
        # if the result set consists of more than one result page.

        for result_sets in search[:self.__PAGE_SIZE]:
            # retrieve the data
            accepted_answer_id = int(self.__is_key_in_json('accepted_answer_id', result_sets.json))
            answer_count = int(self.__is_key_in_json('answer_count', result_sets.json))
            creation_date = result_sets.creation_date
            is_answered = bool(self.__is_key_in_json('is_answered', result_sets.json))
            link = str(self.__is_key_in_json('link', result_sets.json))
            question_id = result_sets.id
            score = result_sets.score
            title = result_sets.title
            view_count = result_sets.view_count
            # check if this question has an owner/user
            if hasattr(result_sets, 'owner'):
                display_name = result_sets.owner.display_name
                profile_link = result_sets.owner.link
                reputation = result_sets.owner.reputation
                user_id = result_sets.owner.id
                user_type = result_sets.owner.user_type
                # create object of the User
                user_obj = StackExchangeUser(display_name, profile_link, reputation, user_id, user_type)
            else:
                user_obj = None
            # create object of the Question
            question_obj = StackExchangeQuestions(accepted_answer_id, answer_count, creation_date, is_answered, link,
                                                  question_id, score, title, view_count, user_obj)
            self.__result_list.append(question_obj)
        return True

    def get_list_of_results(self):
        """
        Returns a list containing the data from the search. Content varies depending on the executed search

        Returns:
             list: List with search result data
        """
        return self.__result_list

    def get_question_data(self, index):
        """
        TODO: function for retrieving question/answer object

        Arguments:
            index:

        Returns:

        """
        obj = self.__result_list[index]

    def __is_key_in_json(self, key=str, json_dict=json):
        """
        Checks if the given key exists in the JSON dictionary

        Arguments:
            key (str): The key to check if exists in the JSON dictionary
            json_dict (json): The JSON object/dictionary to check if contains key

        Returns:
            object: Returns the value belonging to the given key, or ```NO_KEY_VALUE_FOR_ENTRY```

        """
        if key in json_dict:
            # noinspection PyUnresolvedReferences
            return json_dict[key]
        else:
            return self.NO_KEY_VALUE_FOR_ENTRY

    @staticmethod
    def __use_debugging():
        stackexchange.impose_throttling = True
        stackexchange.throttle_stop = False
        stackexchange.web.WebRequestManager.debug = True

    def __convert_user_input_to_stackexchange_site(self, site_name=str):
        """
        Returns the StackExchange site based on ```site_name```

        Arguments:
            site_name (str): Name of site to convert to StackExchange.Site.
                Please note that this is case-sensitive.
                Example: "StackOverflow"

        Returns:
            stackexchange.Site: The selected StackExchange site

        Raises:
            AttributeError: Error if site name is not found

        """
        selected_site = getattr(stackexchange.sites, site_name)
        selected_site = stackexchange.Site(selected_site, self.__STACK_EXCHANGE_KEY)
        return selected_site


class StackExchangeUser(object):
    """
    Object class for creating objects of the ```owner``` data retrieved from StackExchange.
    """

    __display_name = None  # str
    __link = None  # str/url
    __reputation = None  # int
    __user_id = None  # int
    __user_type = None  # str

    def __init__(self, display_name=str, link=str, reputation=int, user_id=int, user_type=str):
        """
        Constructs an object of the Owner data from the returned JSON results
        
        Arguments:
            display_name (str):
            link (str):
            reputation (int):
            user_id (int):
            user_type:
        
        """
        self.__display_name = display_name
        self.__link = link
        self.__reputation = reputation
        self.__user_id = user_id
        self.__user_type = user_type

    def get_display_name(self):
        return self.__display_name

    def get_link(self):
        return self.__link

    def get_reputation(self):
        return self.__reputation

    def get_user_id(self):
        return self.__user_id

    def get_user_type(self):
        return self.__user_type


class StackExchangeQuestions(object):
    """
    Object class for creating objects of the questions retrieved from StackExchange.
    """

    __accepted_answer_id = None  # int
    __answer_count = None  # int
    __creation_date = None  # date (unix epoch time)
    __is_answered = None  # bool
    __link = None  # str (url)
    __question_id = None  # int
    __score = None  # int
    __title = None  # string
    __view_count = None  # int
    __user = None  # object (Owner)

    def __init__(self, accepted_answer_id=int, answer_count=int, creation_date=str, is_answered=bool,
                 link=str, question_id=int, score=int, title=str, view_count=int, user=StackExchangeUser):
        """
        Constructs an object of the Question found at StackExchange
        
        Arguments:
        accepted_answer_id (int):
        answer_count (int):
        creation_date (str):
        is_answered (bool):
        last_activity_date (str):
        last_edit_date (str):
        link (str):
        question_id (int):
        score (int):
        title (str):
        view_count (int):
        owner (Owner):
        
        """
        self.__accepted_answer_id = accepted_answer_id
        self.__answer_count = answer_count
        self.__creation_date = creation_date
        self.__is_answered = is_answered
        self.__link = link
        self.__question_id = question_id
        self.__score = score
        self.__title = title
        self.__view_count = view_count
        self.__user = user

    def get_accepted_answer_id(self):
        return self.__accepted_answer_id

    def get_answer_count(self):
        return self.__answer_count

    def get_creation_date(self):
        return self.__creation_date

    def get_is_answered(self):
        return self.__is_answered

    def get_link(self):
        return self.__link

    def get_question_id(self):
        return self.__question_id

    def get_score(self):
        return self.__score

    def get_title(self):
        return self.__title

    def get_view_count(self):
        return self.__view_count

    def get_user(self):
        return self.__user
