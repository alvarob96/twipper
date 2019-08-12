#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2018-2019 Alvaro Bartolome
# See LICENSE for details.
import datetime
import json

import oauth2
import requests

from twipper.utils import available_languages


def search_tweets(api, oauth_token, plan, label, query, page_count,
                  from_date, to_date, language=None):
    """
    This function retrieves historical tweets on batch processing from Twitter's Full Archive or 30Day. These tweets
    contain the specified words on the query, which can use premium operators as specified on
    https://developer.twitter.com/en/docs/tweets/rules-and-filtering/overview/premium-operators.
    Additionally, some extra arguments can be specified in order to particularize the tweet search, so on to retrieve
    the exact content we are looking for. Retrieved tweets are stored on a :obj:`list` which will lated be returned once
    it is filled with the retrieved tweets.

    Args:
        api (:obj:`oauth2.Client`): valid Twitter API generated via `twipper.credentials.Twipper`.
        oauth_token (:obj:`str`): valid access_token for the authentication of every Twitter Premium API request.
        plan (:obj:`str`): paid plan of twitter premium api, it can either be `30day` or `fullarchive`.
        label (:obj:`str`): label that has been set up for the development environment of the Twitter Premium API.
        query (:obj:`str`): contains the query with the words to search along Twitter historic data.
        page_count (:obj:`int`): specifies the amount of pages (100 tweets per page) to retrieve data from.
        from_date (:obj:`str`): starting date of the time interval to retrieve tweets from (`yyyymmddhhmm` format)
        to_date (:obj:`str`): end date of the time interval to retrieve tweets from (`yyyymmddhhmm` format)
        language (:obj:`str`): is the language on which the tweet has been written.

    Returns:
        tweets (:obj:`list`): description
            Returns a :obj:`list` containing all the retrieved tweets from Twitter, which means all the available tweets
            from the user specified on the arguments of the function.

    Raises:
        ValueError: raised if the introduced arguments do not match or errored.
    """

    if not api or not isinstance(api, oauth2.Client):
        raise ValueError('specified api is not valid!')

    if not oauth_token or not isinstance(oauth_token, str):
        raise ValueError('oauth_token is not valid!')

    if not plan or not isinstance(plan, str):
        raise ValueError('plan must be a `str`!')

    if not label or not isinstance(label, str):
        raise ValueError('label must be a `str`!')

    if not query or not isinstance(query, str):
        raise ValueError('query must be a `str`')

    if not page_count or not isinstance(page_count, int):
        raise ValueError('page_count must be an `int`!')

    if not from_date or not isinstance(from_date, str):
        raise ValueError('from_date must be a `bool`!')

    try:
        datetime.datetime.strptime(from_date, '%Y%m%d%H%M')
    except ValueError:
        raise ValueError('incorrect date format, it should be `yyyymmddhhmm`')

    if not to_date or not isinstance(to_date, str):
        raise ValueError('to_date must be a `bool`!')

    try:
        datetime.datetime.strptime(to_date, '%Y%m%d%H%M')
    except ValueError:
        raise ValueError('incorrect date format, it should be `yyyymmddhhmm`')

    if language and not isinstance(language, str):
        raise ValueError('language must be a `str`!')

    start_date = datetime.datetime.strptime(from_date, '%Y%m%d%H%M')
    end_date = datetime.datetime.strptime(to_date, '%Y%m%d%H%M')

    if start_date >= end_date:
        raise ValueError('incorrect dates, as from_date should be earlier than to_date.')

    url = 'https://api.twitter.com/1.1/tweets/search/' + plan + '/' + label + '.json'

    headers = {
        'Authorization': 'Bearer ' + oauth_token,
        'Content-Type': 'application/json'
    }

    try:
        languages = available_languages(api)
    except (ConnectionError, json.decoder.JSONDecodeError, IndexError):
        raise RuntimeError('`available_languages` function failed.')

    if language:
        if language in languages:
            query += ' lang:' + language
        else:
            raise ValueError('the introduced language does not exist.')

    data = {
        'query': query,
        'fromDate': from_date,
        'toDate': to_date,
        'maxResults': 100
    }

    data = json.dumps(data)

    response = requests.post(url, headers=headers, data=data)

    tweets = list()

    if response.status_code != 200:
        raise ConnectionError('connection to api.twitter could not be established, with error \
        code ' + str(response.status_code))

    result = response.json()

    if 'results' in result:
        tweets += result['results']
    else:
        raise IndexError('no tweets could be retrieved.')

    if 'next' not in result:
        if len(tweets) > 0:
            return tweets
        else:
            raise IndexError(' no tweets could be retrieved.')
    else:
        next_page = result['next']

        for _ in range(page_count - 1):
            data = {
                'query': query,
                'fromDate': from_date,
                'toDate': to_date,
                'maxResults': 100,
                'next': next_page
            }

            data = json.dumps(data)

            response = requests.post(url, headers=headers, data=data)

            if response.status_code != 200:
                break

            result = response.json()

            if 'results' in result:
                tweets += result['results']
            else:
                break

            if 'next' in result:
                next_page = result['next']
            else:
                break

        if len(tweets) > 0:
            return tweets
        else:
            raise IndexError('no tweets could be retrieved.')


def wrapper_premium_user_search(api, oauth_token, plan, label, screen_name,
                                page_count, from_date, to_date, language=None):
    """
    This function retrieves historical tweets on batch processing from Twitter's Full Archive or 30Day from a specific
    user via its screen name (Twitter name). These tweets contain the specified words on the query, which can use
    premium operators as specified on
    https://developer.twitter.com/en/docs/tweets/rules-and-filtering/overview/premium-operators.
    Additionally, some extra arguments can be specified in order to particularize the tweet search, so on to retrieve
    the exact content we are looking for. Retrieved tweets are stored on a :obj:`list` which will lated be returned once
    it is filled with the retrieved tweets.

    Args:
        api (:obj:`oauth2.Client`): valid Twitter API generated via `twipper.credentials.Twipper`.
        oauth_token (:obj:`str`): valid access_token for the authentication of every Twitter Premium API request.
        plan (:obj:`str`): paid plan of twitter premium api, it can either be `30day` or `fullarchive`.
        label (:obj:`str`): label that has been set up for the development environment of the Twitter Premium API.
        screen_name (:obj:`str`):
            is the Twitter's public name of the account that tweets are going to be retrieved, note that the account
            must be public.
        page_count (:obj:`int`): specifies the amount of pages (100 tweets per page) to retrieve data from.
        from_date (:obj:`str`): starting date of the time interval to retrieve tweets from (`yyyymmddhhmm` format)
        to_date (:obj:`str`): end date of the time interval to retrieve tweets from (`yyyymmddhhmm` format)
        language (:obj:`str`): is the language on which the tweet has been written.

    Returns:
        tweets (:obj:`list`): description
            Returns a :obj:`list` containing all the retrieved tweets from Twitter, which means all the available tweets
            from the user specified on the arguments of the function.

    Raises:
        ValueError: raised if the introduced arguments do not match or errored.
    """

    if not api or not isinstance(api, oauth2.Client):
        raise ValueError('specified api is not valid!')

    if not oauth_token or not isinstance(oauth_token, str):
        raise ValueError('oauth_token is not valid!')

    if not plan or not isinstance(plan, str):
        raise ValueError('plan must be a `str`!')

    if not label or not isinstance(label, str):
        raise ValueError('label must be a `str`!')

    if not screen_name or not isinstance(screen_name, str):
        raise ValueError('screen_name must be a `str`')

    if not page_count or not isinstance(page_count, int):
        raise ValueError('page_count must be an `int`!')

    if not from_date or not isinstance(from_date, str):
        raise ValueError('from_date must be a `bool`!')

    try:
        datetime.datetime.strptime(from_date, '%Y%m%d%H%M')
    except ValueError:
        raise ValueError('incorrect date format, it should be `yyyymmddhhmm`')

    if not to_date or not isinstance(to_date, str):
        raise ValueError('to_date must be a `bool`!')

    try:
        datetime.datetime.strptime(to_date, '%Y%m%d%H%M')
    except ValueError:
        raise ValueError('incorrect date format, it should be `yyyymmddhhmm`')

    if language and not isinstance(language, str):
        raise ValueError('language must be a `str`!')

    start_date = datetime.datetime.strptime(from_date, '%Y%m%d%H%M')
    end_date = datetime.datetime.strptime(to_date, '%Y%m%d%H%M')

    if start_date >= end_date:
        raise ValueError('incorrect dates, as from_date should be earlier than to_date.')

    url = 'https://api.twitter.com/1.1/tweets/search/' + plan + '/' + label + '.json'

    query = 'from:' + screen_name

    headers = {
        'Authorization': 'Bearer ' + oauth_token,
        'Content-Type': 'application/json'
    }

    try:
        languages = available_languages(api)
    except (ConnectionError, json.decoder.JSONDecodeError, IndexError):
        raise RuntimeError('`available_languages` function failed.')

    if language:
        if language in languages:
            query += ' lang:' + language
        else:
            raise ValueError('the introduced language does not exist.')

    data = {
        'query': query,
        'fromDate': from_date,
        'toDate': to_date,
        'maxResults': 100
    }

    data = json.dumps(data)

    response = requests.post(url, headers=headers, data=data)

    tweets = list()

    if response.status_code != 200:
        raise ConnectionError('connection to api.twitter could not be established, with error \
            code ' + str(response.status_code))

    result = response.json()

    if 'results' in result:
        tweets += result['results']
    else:
        raise IndexError('no tweets could be retrieved.')

    if 'next' not in result:
        if len(tweets) > 0:
            return tweets
        else:
            raise IndexError(' no tweets could be retrieved.')
    else:
        next_page = result['next']

        for _ in range(page_count - 1):
            data = {
                'query': query,
                'fromDate': from_date,
                'toDate': to_date,
                'maxResults': 100,
                'next': next_page
            }

            data = json.dumps(data)

            response = requests.post(url, headers=headers, data=data)

            if response.status_code != 200:
                break

            result = response.json()

            if 'results' in result:
                tweets += result['results']
            else:
                break

            if 'next' in result:
                next_page = result['next']
            else:
                break

        if len(tweets) > 0:
            return tweets
        else:
            raise IndexError('no tweets could be retrieved.')