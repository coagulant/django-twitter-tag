from __future__ import unicode_literals
import re
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote


def get_user_cache_key(**kwargs):
    """ Generate suitable key to cache twitter tag context
    """
    key = 'get_tweets_%s' % ('_'.join([str(kwargs[key]) for key in sorted(kwargs) if kwargs[key]]))
    not_allowed = re.compile('[^%s]' % ''.join([chr(i) for i in range(33, 128)]))
    key = not_allowed.sub('', key)
    return key


def get_search_cache_key(prefix, *args):
    """ Generate suitable key to cache twitter tag context
    """
    key = '%s_%s' % (prefix, '_'.join([str(arg) for arg in args if arg]))
    not_allowed = re.compile('[^%s]' % ''.join([chr(i) for i in range(33, 128)]))
    key = not_allowed.sub('', key)
    return key


TWITTER_HASHTAG_URL = '<a href="https://twitter.com/search?q=%%23%s">#%s</a>'
TWITTER_USERNAME_URL = '<a href="https://twitter.com/%s">@%s</a>'


def urlize_tweet(tweet):
    """ Turn #hashtag and @username in a text to Twitter hyperlinks,
        similar to the ``urlize()`` function in Django.
    """
    text = tweet.get('html', tweet['text'])
    for hash in tweet['entities']['hashtags']:
        text = text.replace('#%s' % hash['text'], TWITTER_HASHTAG_URL % (quote(hash['text'].encode("utf-8")), hash['text']))
    for mention in tweet['entities']['user_mentions']:
        text = text.replace('@%s' % mention['screen_name'], TWITTER_USERNAME_URL % (quote(mention['screen_name']), mention['screen_name']))
    tweet['html'] = text
    return tweet


def expand_tweet_urls(tweet):
    """ Replace shortened URLs with long URLs in the twitter status, and add the "RT" flag.
        Should be used before urlize_tweet
    """
    if 'retweeted_status' in tweet:
        text = 'RT @{user}: {text}'.format(user=tweet['retweeted_status']['user']['screen_name'],
                                           text=tweet['retweeted_status']['text'])
        urls = tweet['retweeted_status']['entities']['urls']
    else:
        text = tweet['text']
        urls = tweet['entities']['urls']

    for url in urls:
        text = text.replace(url['url'], '<a href="%s">%s</a>' % (url['expanded_url'], url['display_url']))
    tweet['html'] = text
    return tweet