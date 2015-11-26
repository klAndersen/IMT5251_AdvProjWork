import json
import stackexchange

"""
This file contains all classes that are used to objectify, handle and process search results.
It can be debated whether or not creating my own objects is a good idea, since the Py-StackExchange comes with its own
models, see: https://github.com/lucjon/Py-StackExchange/blob/master/stackexchange/models.py

The problem with this however, is that the format returns the Question model, which leads to me not being able
to retrieve the currently accepted answer (presuming there is one). For this project, I think the code will be as-is,
but this may be updated and changed during my Master thesis.

As for the comment marked '# noinspection PyUnresolvedReferences', this is used to disable warning from PyCharm.
"""

_author_ = "Knut Lucas Andersen"


class SearchStackExchange:
    """
    Class for searching and returning results from StackExchange by using the py-stackexchange API.

    The main goal of this class is to handle search, lookup answers and all other required interactions
    with the StackExchange community
    """

    NO_KEY_VALUE_FOR_ENTRY = -1

    def __init__(self):
        self.__result_list = list()

    def process_search_results_for_question(self, site=stackexchange.Site, question=str):
        """
        Runs a search against the given site, looking for the given question and returns
        the object containing the search data.

        Arguments:
            site (stackexchange.Site): The site to search for the given question
            question (str): The question to search for
        See:
                ```stackexchange.Site.search```
        Returns:
            bool || stackexchange.Site.search: Returns ```False``` if search had no results (or failed).
            If search was successful, the resultset of the search is returned.
            If you want the processed results, call ```get_list_of_results```

        """
        search = site.search(intitle=question)
        if (search is None) or (len(search.items) == 0):
            return False

        # TODO: Figure out why the loop returns duplicates (loops through the same page twice)
        # TODO: Throttle error occurred approx 03:40 am
        # TODO: Ask Simon about Tuple looping; perhaps the error is in the loop?

        for result_sets in search:
            # TODO: REMOVE THIS
            if hasattr(result_sets, 'owner'):
                print(result_sets.owner.display_name)
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
        return search

    def get_list_of_results(self):
        """
        Returns a list containing the data from the search. The content varies depending on the executed search

        Returns:
             list: List with search result data
        """
        return self.__result_list

    def __is_key_in_json(self, key=str, json_dict=json):
        """

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

# selected_site = stackexchange.Site(stackexchange.StackOverflow)
# # TODO: Turn off debugging options
# stackexchange.impose_throttling = True
# stackexchange.throttle_stop = False
# stackexchange.web.WebRequestManager.debug = True
# search_stackexchange = SearchStackExchange()
# res_obj = None
# # was the search executed successfully?
# search_result = search_stackexchange.process_search_results_for_question(selected_site, 'how to increment') #'Py-StackExchange filter by tag') #
# if type(search_result) is bool and search_result is False:
#     result = "No results found matching asked question."
# else:
#     # test question: 'Py-StackExchange filter by tag'
#     res_list = search_stackexchange.get_list_of_results()
#     if len(res_list) == 1:
#         res_obj = res_list[0]
#     else:
#         # TODO: handle multiple results here.. for now, just retrieve the first one
#         res_obj = res_list[0]
# if res_obj is not None:
#     print(res_obj.get_user().get_display_name())
