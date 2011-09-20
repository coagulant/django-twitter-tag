from django import template
from django.conf import settings
from templatetag_sugar.parser import Optional, Constant, Name, Variable
from templatetag_sugar.register import tag
import ttp
import twitter


register = template.Library()


@tag(register, [Constant("for"), Variable(), Constant("as"), Name(),
                Optional([Constant("exclude"), Variable("exclude")]),
                Optional([Constant("limit"), Variable("limit")])])
def get_tweets(context, username, asvar, exclude='', limit=None):

    p = ttp.Parser()
    tweets = []
    include_rts = 'retweets' not in exclude
    try:
        user_last_tweets = twitter.Api().GetUserTimeline(screen_name=username,
                                                         include_rts=include_rts,
                                                         include_entities=True)
    except twitter.TwitterError:
        if settings.DEBUG:
            raise
        context[asvar] = []
        return ""

    for status in user_last_tweets:
        if 'replies' in exclude and status.GetInReplyToUserId() is not None:
            continue

        status.html = p.parse(status.GetText()).html
        tweets.append(status)

    if limit:
        tweets = tweets[:limit]

    context[asvar] = tweets

    return ""