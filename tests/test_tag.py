# coding: utf-8
from __future__ import unicode_literals
import json
import os
import unittest
import warnings
import datetime

from mock import patch
from sure import expect
from django.conf import settings
from django.core.cache import cache
from django.template import Context, Template, TemplateSyntaxError
from httpretty import httprettified, HTTPretty

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
            length = len(json.loads(get_json(json_mock)))
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
        self.assertRaises(TemplateSyntaxError, Template, """{% get_tweets %}""")
        self.assertRaises(TemplateSyntaxError, Template, """{% get_tweets as "tweets" %}""")

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
        cache_key = get_user_cache_key('jresig', 'tweets')
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
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            output, context = self.render(
                template="""{% get_tweets for "jresig" as tweets exclude 'replies, retweets' %}""",
                json_mocks=['jeresig.json'],
            )
            assert len(w) == 0

    @httprettified
    def test_datetime(self):
        output, context = self.render(
            template="""{% get_tweets for "jresig" as tweets %}""",
            json_mocks='jeresig.json',
        )
        # Fri Mar 21 19:42:21 +0000 2008
        self.assertEquals(context['tweets'][0]['datetime'], datetime.datetime(2008, 3, 21, 19, 42, 21))

    @httprettified
    def test_html(self):
        output, context = self.render(
            template="""{% get_tweets for "jresig" as tweets %}""",
            json_mocks='jeresig.json',
        )
        self.assertEquals(context['tweets'][0]['html'], """This is not John Resig - you should be following <a href=\"http://twitter.com/jeresig\">@jeresig</a> instead!!!""")

    @httprettified
    def test_expand_urlize(self):
        output, context = self.render(
            template="""{% get_tweets for "futurecolors" as tweets %}""",
            json_mocks='futurecolors.json',
        )
        tweet = context['tweets'][0]

        self.assertTrue(tweet['text'].endswith('...'))  # original response is trimmed by api...
        self.assertFalse(tweet['html'].endswith('...'))  # but not ours html ;)
        self.assertTrue(tweet['html'].startswith('RT <a href="http://twitter.com/travisci">@travisci</a>: '))

    @httprettified
    def test_url_is_not_expanded(self):
        output, context = self.render(
            template="""{% get_tweets for "futurecolors" as tweets max_url_length 0 %}""",
            json_mocks='futurecolors.json',
        )
        tweet = context['tweets'][0]
        expect(tweet['html']).to.contain('http://t.co/aVQRnBKP')
        expect(tweet['html']).to.contain('http://t.co/7KgHV8iI')


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


def render_template(template):
    context = Context()
    template = Template('{% load twitter_tag %}'+template)
    output = template.render(context)
    return output, context


def clear_query_dict(query):
    oauth_keys = [
        'oauth_consumer_key',
        'oauth_nonce',
        'oauth_signature',
        'oauth_signature_method',
        'oauth_timestamp',
        'oauth_token',
        'oauth_version'
    ]
    return dict((k, v) for k, v in query.iteritems() if k not in oauth_keys)


def get_json(somefile):
    return open(os.path.join('tests', 'json', somefile)).read()
