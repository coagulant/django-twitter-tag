# coding: utf-8
from __future__ import unicode_literals
import json
import unittest
import warnings
import datetime

from mock import patch
from nose.tools import nottest
from sure import expect
from django.conf import settings
from django.core.cache import cache
from django.template import Template, TemplateSyntaxError
from django.utils import timezone
from httpretty import httprettified, HTTPretty
from tests.utils import render_template, clear_query_dict, get_json

from twitter_tag.utils import get_user_cache_key


class TwitterTag(unittest.TestCase):
    api_url = None
    logger_name = 'twitter_tag.templatetags.twitter_tag'

    @httprettified
    def check_render(self, template, json_mock, expected_kwargs, length=None, asvar='tweets'):
        output, context = self.render(template, json_mock)

        expect(output).should.be.empty
        expect(clear_query_dict(HTTPretty.last_request.querystring)).should.equal(expected_kwargs)
        if length is None:
            length = len(json.loads(get_json(json_mock).decode('utf8')))
        expect(context[asvar]).should.have.length_of(length)
        return context

    def render(self, template, json_mocks):
        if type(json_mocks) is not list:
            json_mocks = [json_mocks]
        responses = [HTTPretty.Response(get_json(_)) for _ in json_mocks]

        HTTPretty.register_uri(HTTPretty.GET, self.api_url, responses=responses, content_type='application/json')
        return render_template(template=template)


@patch.multiple(settings, TWITTER_OAUTH_TOKEN='foo', TWITTER_OAUTH_SECRET='bar',
                TWITTER_CONSUMER_KEY='baz', TWITTER_CONSUMER_SECRET='Alice', create=True)
class UsernameTag(TwitterTag):
    api_url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'

    def test_no_args(self):
        context = self.check_render(
            template="""{% get_tweets for "jresig" as tweets %}""",
            json_mock='jeresig.json',
            expected_kwargs={'screen_name': ['jresig']},
        )
        expect(context['tweets'][0]['text']).to.equal("This is not John Resig - you should be following @jeresig instead!!!")

    def test_limit(self):
        self.check_render(
            template="""{% get_tweets for "futurecolors" as tweets limit 2 %}""",
            json_mock='coagulant.json',
            expected_kwargs={'screen_name': ['futurecolors']},
            length=2
        )

    def test_exclude_replies(self):
        self.check_render(
            template="""{% get_tweets for "futurecolors" as tweets exclude 'replies' %}""",
            json_mock='coagulant.json',
            expected_kwargs={'screen_name': ['futurecolors'], 'exclude_replies': ['True']},
        )

    def test_exclude_retweets(self):
        self.check_render(
            template="""{% get_tweets for "coagulant" as tweets exclude 'retweets' %}""",
            json_mock='coagulant.json',
            expected_kwargs={'screen_name': ['coagulant'], 'include_rts': ['False']},
        )

    def test_exclude_all(self):
        self.check_render(
            template="""{% get_tweets for "coagulant" as tweets exclude 'replies,rts' %}""",
            json_mock='coagulant.json',
            expected_kwargs={'screen_name': ['coagulant'], 'exclude_replies': ['True'], 'include_rts': ['False']},
        )

    @httprettified
    def test_several_twitter_tags_on_page(self):
        output, context = self.render(
            template="""{% get_tweets for "jresig" as tweets %}{% get_tweets for "coagulant" as more_tweets %}""",
            json_mocks=['jeresig.json', 'coagulant.json'],
        )
        expect(output).should.be.empty
        expect(context['tweets']).should.have.length_of(1)
        expect(context['more_tweets']).should.have.length_of(3)

    def test_bad_syntax(self):
        Template.when.called_with("""{% get_tweets %}""").should.throw(TemplateSyntaxError)
        Template.when.called_with("""{% get_tweets as "tweets" %}""").should.throw(TemplateSyntaxError)

    @patch('logging.getLogger')
    @httprettified
    def test_exception_is_not_propagated_but_logged(self, logging_mock):
        exception_message = 'Capacity Error'
        HTTPretty.register_uri(HTTPretty.GET, self.api_url, body=exception_message, status=503, content_encoding='identity')
        output, context = render_template("""{% get_tweets for "twitter" as tweets %}""")
        expect(output).should.be.empty
        expect(context['tweets']).should.be.empty

        logging_mock.assert_called_with(self.logger_name)
        expect(logging_mock.return_value.error.call_args[0][0]).should.contain(exception_message)

    @patch('logging.getLogger')
    @httprettified
    def test_get_from_cache_when_twitter_api_fails(self, logging_mock):
        exception_message = 'Too many requests'
        HTTPretty.register_uri(HTTPretty.GET, self.api_url,
                               responses=[
                                   HTTPretty.Response(body=get_json('jeresig.json'), status=200, content_encoding='identity'),
                                   HTTPretty.Response(body=exception_message, status=429, content_encoding='identity'),
                               ])

        # it should be ok by now
        output, context = render_template("""{% get_tweets for "jresig" as tweets %}""")
        cache_key = get_user_cache_key(asvar='tweets', username='jresig')
        expect(cache.get(cache_key)).should.have.length_of(1)
        expect(context['tweets'][0]['text']).to.equal("This is not John Resig - you should be following @jeresig instead!!!")

        # when twitter api fails, should use cache
        output2, context2 = render_template("""{% get_tweets for "jresig" as tweets %}""")
        expect(cache.get(cache_key)).should.have.length_of(1)
        expect(context2['tweets'][0]['text']).to.equal("This is not John Resig - you should be following @jeresig instead!!!")
        logging_mock.assert_called_with(self.logger_name)
        expect(logging_mock.return_value.error.call_args[0][0]).should.contain(exception_message)

    @httprettified
    def test_cache_key_portable(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            output, context = self.render(
                template="""{% get_tweets for "jresig" as tweets exclude 'replies, retweets' %}""",
                json_mocks=['jeresig.json'],
            )
            assert len(caught_warnings) == 0

    @httprettified
    def test_datetime(self):
        output, context = self.render(
            template="""{% get_tweets for "jresig" as tweets %}""",
            json_mocks='jeresig.json',
        )
        # Fri Mar 21 19:42:21 +0000 2008
        if settings.USE_TZ:
            # Get utc.
            (context['tweets'][0]['datetime']).should.be.equal(datetime.datetime(2008, 3, 21, 19, 42, 21).replace(tzinfo=timezone.utc))
        else:
            (context['tweets'][0]['datetime']).should.be.equal(datetime.datetime(2008, 3, 21, 19, 42, 21))


    @httprettified
    def test_html_mentions(self):
        output, context = self.render(
            template="""{% get_tweets for "jresig" as tweets %}""",
            json_mocks='jeresig.json',
        )
        (context['tweets'][0]['html']).should.be.equal("""This is not John Resig - you should be following <a href=\"https://twitter.com/jeresig\">@jeresig</a> instead!!!""")

    @httprettified
    def test_expand_urlize(self):
        output, context = self.render(
            template="""{% get_tweets for "futurecolors" as tweets %}""",
            json_mocks='futurecolors.json',
        )
        tweet = context['tweets'][0]

        expect(tweet['text'].endswith('...')).should.be.true  # original response is trimmed by api...
        expect(tweet['html'].endswith('...')).should.be.false  # but not ours html ;)
        expect(tweet['html'].startswith('RT <a href="https://twitter.com/travisci">@travisci</a>: ')).should.be.true


def test_settings():
    render_template.when.called_with('{% get_tweets for "futurecolors" as tweets %}').should.throw(AttributeError)


@patch.multiple(settings, TWITTER_OAUTH_TOKEN='foo', TWITTER_OAUTH_SECRET='bar',
                TWITTER_CONSUMER_KEY='baz', TWITTER_CONSUMER_SECRET='Alice', create=True)
class SearchTag(TwitterTag):
    api_url = 'https://api.twitter.com/1.1/search/tweets.json'

    def test_search(self):
        self.check_render(
            template="""{% search_tweets for "python 3" as tweets %}""",
            json_mock='python3.json',
            expected_kwargs={'q': ['python 3']},
            length=15
        )

    def test_custom_args(self):
        self.check_render(
            template="""{% search_tweets for "python 3" as tweets lang='eu' result_type='popular' %}""",
            json_mock='python3.json',
            expected_kwargs={'q': ['python 3'], 'lang': ['eu'], 'result_type': ['popular']},
            length=15
        )

    @httprettified
    def test_html_hashtags(self):
        output, context = self.render(
            template="""{% search_tweets for "python 3" as tweets %}""",
            json_mocks='python3.json',
        )
        tweet_html = context['tweets'][0]['html']
        expect(tweet_html).should.contain('<a href="https://twitter.com/search?q=%23python">#python')
        expect(tweet_html).should.contain('<a href="https://twitter.com/search?q=%23%D0%9A%D0%B0%D1%83%D1%87%D0%94%D0%91">#КаучДБ')

    @nottest  # https://github.com/gabrielfalcao/HTTPretty/issues/36')
    @httprettified
    def test_unicode_query(self):
        self.check_render(
            template=u"""{% search_tweets for "питон" as tweets %}""",
            json_mock='python3.json',
            expected_kwargs={'q': ['питон']},
            length=15
        )