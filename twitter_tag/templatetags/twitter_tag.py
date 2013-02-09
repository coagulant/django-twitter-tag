from __future__ import unicode_literals
from datetime import datetime
import logging

from django import template
from django.conf import settings
from django.core.cache import cache

from twitter import Twitter, OAuth, TwitterError
from classytags.core import Tag, Options
from classytags.arguments import Argument, MultiKeywordArgument

from ..utils import expand_tweet_urls, urlize_twitter_text, get_user_cache_key, get_search_cache_key


register = template.Library()


class BaseTwitterTag(Tag):
    """ Abstract twitter tag"""

    def get_cache_key(self, args_disct):
        raise NotImplemented

    def get_json(self, twitter):
        raise NotImplemented

    def get_api_call_params(self, **kwargs):
        raise NotImplemented

    def enrich(self, tweet, max_url_length):
        """ Apply the local presentation logic to the fetched data."""
        text = expand_tweet_urls(tweet, max_url_length)
        tweet['html'] = urlize_twitter_text(text, max_url_length)
        # parses created_at "Wed Aug 27 13:08:45 +0000 2008"
        tweet['datetime'] = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        return tweet

    def render_tag(self, context, **kwargs):
        cache_key = self.get_cache_key(kwargs)
        max_url_length = 60 if kwargs['max_url_length'] is None else kwargs['max_url_length']

        try:
            twitter = Twitter(auth=OAuth(settings.TWITTER_OAUTH_TOKEN,
                                         settings.TWITTER_OAUTH_SECRET,
                                         settings.TWITTER_CONSUMER_KEY,
                                         settings.TWITTER_CONSUMER_SECRET))
            json = self.get_json(twitter, **self.get_api_call_params(**kwargs))
        except TwitterError as e:
            logging.getLogger(__name__).error(str(e))
            context[kwargs['asvar']] = cache.get(cache_key, [])
            return ''

        json = [self.enrich(tweet, max_url_length) for tweet in json]

        if kwargs['limit']:
            json = json[:kwargs['limit']]
        context[kwargs['asvar']] = json
        cache.set(cache_key, json)

        return ''


class UserTag(BaseTwitterTag):
    """ A django template tag to display user's recent tweets.

        :type context: list
        :type username: string
        :type asvar: string
        :type exclude: string
        :type max_url_length: string
        :type limit: string

        NB: count argument of twitter API is not useful, so we slice it ourselves
            "We include retweets in the count, even if include_rts is not supplied.
             It is recommended you always send include_rts=1 when using this API method."

        Examples:
        {% get_tweets for "futurecolors" as tweets exclude "replies" limit 10 %}
        {% get_tweets for "futurecolors" as tweets exclude "retweets" %}
        {% get_tweets for "futurecolors" as tweets max_url_length 0 %}
        {% get_tweets for "futurecolors" as tweets exclude "retweets,replies" max_url_length 20 limit 1 %}
    """
    name = 'get_tweets'
    options = Options(
        'for', Argument('username'),
        'as', Argument('asvar', resolve=False),
        'exclude', Argument('exclude', required=False),
        'max_url_length', Argument('max_url_length', required=False),
        'limit', Argument('limit', required=False),
    )

    def get_cache_key(self, kwargs_dict):
        return get_user_cache_key(*kwargs_dict.values())

    def get_api_call_params(self, **kwargs):
        params = {'screen_name': kwargs['username']}
        if kwargs['exclude']:
            if 'replies' in kwargs['exclude']:
                params['exclude_replies'] = True
            if 'retweets' in kwargs['exclude'] or 'rts' in kwargs['exclude']:
                params['include_rts'] = False
        return params

    def get_json(self, twitter, **kwargs):
        return twitter.statuses.user_timeline(**kwargs)


class SearchTag(BaseTwitterTag):
    name = 'search_tweets'
    options = Options(
        'for', Argument('q'),
        'as', Argument('asvar', resolve=False),
        MultiKeywordArgument('options', required=False),
        'max_url_length', Argument('max_url_length', required=False),
        'limit', Argument('limit', required=False),
    )

    def get_cache_key(self, kwargs_dict):
        return get_search_cache_key(*kwargs_dict.values())

    def get_api_call_params(self, **kwargs):
        params = {'q': kwargs['q']}
        params.update(kwargs['options'])
        return params

    def get_json(self, twitter, **kwargs):
        return twitter.search.tweets(**kwargs)['statuses']


register.tag(UserTag)
register.tag(SearchTag)


