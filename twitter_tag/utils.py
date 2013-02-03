from __future__ import unicode_literals
import re
import ttp


def get_user_cache_key(*args):
    """ Generate suitable key to cache twitter tag context
    """
    key = 'get_tweets_%s' % ('_'.join([str(arg) for arg in args if arg]))
    not_allowed = re.compile('[^%s]' % ''.join([chr(i) for i in xrange(33, 128)]))
    key = not_allowed.sub('', key)
    return key


def get_search_cache_key(prefix, *args):
    """ Generate suitable key to cache twitter tag context
    """
    key = '%s_%s' % (prefix, '_'.join([str(arg) for arg in args if arg]))
    not_allowed = re.compile('[^%s]' % ''.join([chr(i) for i in xrange(33, 128)]))
    key = not_allowed.sub('', key)
    return key


def urlize_twitter_text(text, max_url_length=60):
    """ Turn #hashtag and @username in a text to Twitter hyperlinks,
        similar to the ``urlize()`` function in Django.
    """
    tweet_parser = ttp.Parser(max_url_length=max_url_length)
    return tweet_parser.parse(text).html


def expand_tweet_urls(status, max_url_length=60):
    """ Replace shortened URLs with long URLs in the twitter status, and add the "RT" flag. """
    if 'retweeted_status' in status:
        text = 'RT @{user}: {text}'.format(user=status['retweeted_status']['user']['screen_name'],
                                           text=status['retweeted_status']['text'])
        urls = status['retweeted_status']['entities']['urls']
    else:
        text = status['text']
        urls = status['entities']['urls']

    if max_url_length:
        for status_url in urls:
            text = text.replace(status_url['url'], status_url['expanded_url'])

    return text