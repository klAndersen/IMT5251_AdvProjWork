import json
import stackexchange as StackExchange

"""
This file contains all classes that are used to objectify, handle and process search results.
It can be debated whether or not creating my own objects is a good idea, since the Py-StackExchange comes with its own
models, see: https://github.com/lucjon/Py-StackExchange/blob/master/stackexchange/models.py

The problem with this however, is that the format returns the Question model, which leads to me not being able
to retrieve the currently accepted answer (presuming there is one). For this project, I think the code will be as-is,
but this may be updated and changed during my Master thesis.

As for the comments marked '# noinspection PyUnresolvedReferences', these are to disable warnings from PyCharm.
"""

_author_ = "Knut Lucas Andersen"


class SearchStackExchange:
    """
    Class for searching and returning results from StackExchange by using the py-stackexchange API.

    The main goal of this class is to handle search, lookup answers and all other required interactions
    with the StackExchange community
    """

    def __init__(self):
        self.__result_list = list()

    def process_search_results_for_question(self, site=StackExchange.Site, question=str):
        """
        Runs a search against the given site, looking for the given question and returns
        the object containing the search data.

        Arguments:
            site (stackexchange.Site): The site to search for the given question
            question (str): The question to search for
        See:
                ```stackexchange.Site.search```
        Returns:
            stackexchange.Site.search: The resultset of the search.
                                        If you want the processed results, call ```get_list_of_results```

        """
        search = site.search(intitle=question)
        search.fetch()
        if search is None or search.items is None:
            return "No results found matching asked question."

        # TODO: Handle multiple results returned (e.g. pagecount > limit)

        for result_sets in search:
            items_obj = self.__create_items_object(result_sets.json)
            self.__result_list.append(items_obj)
        return search
    
    def __create_items_object(self, json_dict=json):
        """
        Retrieves the ```items``` data from the JSON dictionary and adds it to the object for easy retrieval

        Arguments:
            json_dict (json): JSON dictionary with ```items``` data

        """
        # noinspection PyUnresolvedReferences
        accepted_answer_id = json_dict['accepted_answer_id']
        # noinspection PyUnresolvedReferences
        answer_count = json_dict['answer_count']
        # noinspection PyUnresolvedReferences
        creation_date = json_dict['creation_date']
        # noinspection PyUnresolvedReferences
        is_answered = json_dict['is_answered']
        # noinspection PyUnresolvedReferences
        last_activity_date = json_dict['last_activity_date']
        # noinspection PyUnresolvedReferences
        last_edit_date = json_dict['last_edit_date']
        # noinspection PyUnresolvedReferences
        link = json_dict['link']
        # noinspection PyUnresolvedReferences
        question_id = json_dict['question_id']
        # noinspection PyUnresolvedReferences
        score = json_dict['score']
        # noinspection PyUnresolvedReferences
        title = json_dict['title']
        # noinspection PyUnresolvedReferences
        view_count = json_dict['view_count']
        # noinspection PyUnresolvedReferences
        owner = self.__create_owner_object(json_dict['owner'])
        items_obj = Items(accepted_answer_id, answer_count, creation_date, is_answered, last_activity_date,
                          last_edit_date, link, question_id, score, title, view_count, owner)
        return items_obj

    @staticmethod
    def __create_owner_object(json_dict=json):
        """
        Retrieves the ```owner``` data from the JSON dictionary and adds it to the object for easy retrieval

        Arguments:
            json_dict (json): JSON dictionary with ```owner``` data

        Returns:
            Owner: Class object based on data from JSON

        """
        # noinspection PyUnresolvedReferences
        accept_rate = json_dict['accept_rate']
        # noinspection PyUnresolvedReferences
        display_name = json_dict['display_name']
        # noinspection PyUnresolvedReferences
        link = json_dict['link']
        # noinspection PyUnresolvedReferences
        profile_image = json_dict['profile_image']
        # noinspection PyUnresolvedReferences
        reputation = json_dict['reputation']
        # noinspection PyUnresolvedReferences
        user_id = json_dict['user_id']
        # noinspection PyUnresolvedReferences
        user_type = json_dict['user_type']
        owner_obj = Owner(accept_rate, display_name, link, profile_image, reputation, user_id, user_type)
        return owner_obj

    def get_list_of_results(self):
        """
        Returns a list containing the data from the search. The content varies depending on the executed search

        Returns:
             list: List with search result data
        """
        return self.__result_list


class Owner(object):
    """
    Object class for creating objects of the ```owner``` data retrieved from StackExchange.
    """

    __accept_rate = None  # int
    __display_name = None  # str
    __link = None  # str/url
    __profile_image = None  # str/url
    __reputation = None  # int
    __user_id = None  # int
    __user_type = None  # str

    def __init__(self, accept_rate=int, display_name=str, link=str, profile_image=str, reputation=int,
                 user_id=int, user_type=str):
        """
        Constructs an object of the Owner data from the returned JSON results
        
        Arguments:
            accept_rate (int):
            display_name (str):
            link (str):
            profile_image (str):
            reputation (int):
            user_id (int):
            user_type:
        
        """
        self.__accept_rate = accept_rate
        self.__display_name = display_name
        self.__link = link
        self.__profile_image = profile_image
        self.__reputation = reputation
        self.__user_id = user_id
        self.__user_type = user_type

    def get_accept_rate(self):
        return self.__accept_rate

    def get_display_name(self):
        return self.__display_name

    def get_link(self):
        return self.__link

    def get_profile_image(self):
        return self.__profile_image

    def get_reputation(self):
        return self.__reputation

    def get_user_id(self):
        return self.__user_id

    def get_user_type(self):
        return self.__user_type


class Items(object):

    __accepted_answer_id = None  # int
    __answer_count = None  # int
    __creation_date = None  # date (unix epoch time)
    __is_answered = None  # bool
    __last_activity_date = None  # date (unix epoch time)
    __last_edit_date = None  # date (unix epoch time)
    __link = None  # str (url)
    __question_id = None  # int
    __score = None  # int
    __title = None  # string
    __view_count = None  # int
    __owner = None  # object (Owner)

    def __init__(self, accepted_answer_id=int, answer_count=int, creation_date=str, is_answered=bool,
                 last_activity_date=str, last_edit_date=str, link=str, question_id=int, score=int,
                 title=str, view_count=int, owner=Owner):
        """
        
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
        self.__last_activity_date = last_activity_date
        self.__last_edit_date = last_edit_date
        self.__link = link
        self.__question_id = question_id
        self.__score = score
        self.__title = title
        self.__view_count = view_count
        self.__owner = owner

    def get_accepted_answer_id(self):
        return self.__accepted_answer_id

    def get_answer_count(self):
        return self.__answer_count

    def get_creation_date(self):
        return self.__creation_date

    def get_is_answered(self):
        return self.__is_answered

    def get_last_activity_date(self):
        return self.__last_activity_date

    def get_last_edit_date(self):
        return self.__last_edit_date

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

    def get_owner(self):
        return self.__owner
