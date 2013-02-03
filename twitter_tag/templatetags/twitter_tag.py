from __future__ import unicode_literals
from datetime import datetime
import logging

from django import template
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured

from twitter import Twitter, OAuth, TwitterError
from classytags.core import Tag, Options
from classytags.arguments import Argument

from ..utils import expand_tweet_urls, urlize_twitter_text, get_cache_key


register = template.Library()
OAUTH_TOKEN = getattr(settings, 'TWITTER_OAUTH_TOKEN', None)
OAUTH_SECRET = getattr(settings, 'TWITTER_OAUTH_SECRET', None)
CONSUMER_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', None)
CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', None)


class TwitterTag(Tag):
    """ A django template tag to display user's recent tweets.

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

    def enrich(self, tweet, max_url_length):
        """ Apply the local presentation logic to the fetched data."""
        text = expand_tweet_urls(tweet, max_url_length)
        tweet['html'] = urlize_twitter_text(text, max_url_length)
        # parses created_at "Wed Aug 27 13:08:45 +0000 2008"
        tweet['datetime'] = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        return tweet

    # noinspection PyMethodOverriding
    def render_tag(self, context, username, asvar, exclude=None, max_url_length=None, limit=None):
        """ Renders tag, captain obvious.
            :type context: list
            :type username: string
            :type asvar: string
            :type exclude: string
            :type max_url_length: string
            :type limit: string

            NB: count argument of twitter API is not useful, so we slice it ourselves
                "We include retweets in the count, even if include_rts is not supplied.
                 It is recommended you always send include_rts=1 when using this API method."
        """
        kwargs = {}
        cache_key = get_cache_key(username, asvar, exclude, limit)
        if exclude:
            if 'replies' in exclude:
                kwargs['exclude_replies'] = True
            if 'retweets' in exclude or 'rts' in exclude:
                kwargs['include_rts'] = False
        if max_url_length is None:
            max_url_length = 60

        try:
            if not all([OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET]):
                raise ImproperlyConfigured('Missing settings key')
            twitter = Twitter(auth=OAuth(OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET))
            json = twitter.statuses.user_timeline(screen_name=username, **kwargs)
        except TwitterError as e:
            logging.getLogger(__name__).error(str(e))
            context[asvar] = cache.get(cache_key, [])
            return ''

        json = [self.enrich(tweet, max_url_length) for tweet in json]

        if limit:
            json = json[:limit]
        context[asvar] = json
        cache.set(cache_key, json)

        return ''


register.tag(TwitterTag)