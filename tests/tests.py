# -*- coding: utf-8 -*-
import collections
from django.conf import settings
from django.template import Template, Context
from django.template.base import TemplateSyntaxError
from django.test import TestCase
from mock import patch
import twitter


class StubGenerator(object):
    TWEET_STUBS = {'jresig': [{'text': "This is not John Resig - you should be following @jeresig instead!",
                               'html': "This is not John Resig - you should be following <a href=\"http://twitter.com/jeresig\">@jeresig</a> instead!"}],
                   'futurecolors': [{'text': u"JetBrains радуют новыми фичами и апдейтами старых. Пост из блога #pycharm про дебаг шаблонов джанги в их IDE http://ht.ly/6viu3"},
                                    {'text': u"На новых проектах будем использовать django-jenkins и django-any http://t.co/FjhHpdwV http://t.co/Hig8Hsjg Очень полезные штуки."},
                                    {'text': u"@goshakkk Переход на руби был связан именно с отсутствием поддержки py3k? :)",
                                     'in_reply_to_user_id': 61236914},
                                    {'text': u"Наконец-то начались какие-то попытки портировать #Django на #python3 http://t.co/XkftDsQH",
                                     'retweeted': True},
                                   ]
                  }

    @classmethod
    def get_timeline(cls, screen_name, include_rts, **kwargs):
        user = cls.get_user(screen_name=screen_name)
        tweets = []
        for stub in cls.TWEET_STUBS[screen_name]:
            if not include_rts and stub.get('retweeted', False):
                continue
            html = stub.pop('html', '')
            tweet = cls.get_status(user=user, **stub)
            tweet.html = html
            tweets.append(tweet)
        return tweets

    @classmethod
    def get_user(cls, screen_name, **kwargs):
        return twitter.User(screen_name=screen_name, **kwargs)

    @classmethod
    def get_status(cls, **kwargs):
        return twitter.Status(**kwargs)


class TwitterTagTestCase(TestCase):

    def setUp(self):
        patcher = patch('twitter.Api')
        self.addCleanup(patcher.stop)
        mock = patcher.start()
        self.api = mock.return_value
        self.api.GetUserTimeline.side_effect = StubGenerator.get_timeline

    def render_template(self, template):
        context = Context()
        template = Template(template)
        output = template.render(context)
        return output, context

    def test_twitter_tag_simple_mock(self):
        output, context = self.render_template(template="""{% load twitter_tag %}{% get_tweets for "jresig" as tweets %}""")

        self.api.GetUserTimeline.assert_called_with(screen_name='jresig', include_rts=True, include_entities=True)
        self.assertEquals(len(context['tweets']), 1, 'jresig account has only one tweet')
        self.assertEquals(output, '')
        self.assertEquals(context['tweets'][0].text,
                          'This is not John Resig - you should be following @jeresig instead!',
                          'one and only tweet text')
        self.assertEquals(context['tweets'][0].html,
                          'This is not John Resig - you should be following <a href="http://twitter.com/jeresig">@jeresig</a> instead!',
                          'corresponding html for templates')

    def test_several_twitter_tags_on_page(self):
        output, context = self.render_template(template="""{% load twitter_tag %}
                                                           {% get_tweets for "jresig" as tweets %}
                                                           {% get_tweets for "futurecolors" as more_tweets %}""")
        self.assertEqual(output.strip(), '')
        self.assertEquals(len(context['tweets']), 1, 'jresig account has only one tweet')
        self.assertEqual(context['tweets'][0].text, StubGenerator.TWEET_STUBS['jresig'][0]['text'])

        self.assertEquals(len(context['more_tweets']), 4, 'futurecolors have 4 tweets')
        self.assertEqual(context['more_tweets'][0].text, StubGenerator.TWEET_STUBS['futurecolors'][0]['text'])
        
    def test_twitter_tag_limit(self):
        output, context = self.render_template(
            template="""{% load twitter_tag %}{% get_tweets for "futurecolors" as tweets limit 2 %}""")

        self.api.GetUserTimeline.assert_called_with(screen_name='futurecolors', include_rts=True, include_entities=True)
        self.assertEquals(len(context['tweets']), 2, 'Context should have 2 tweets')

    def test_twitter_tag_with_no_replies(self):
        output, context = self.render_template(
            template="""{% load twitter_tag %}{% get_tweets for "futurecolors" as tweets exclude "replies" limit 10 %}""")

        self.api.GetUserTimeline.assert_called_with(screen_name='futurecolors', include_rts=True, include_entities=True)
        self.assertEquals(len(context['tweets']), 3, 'Stub contains 4 tweets, including 1 reply')

        tweets_context = collections.deque(context['tweets'])
        for stub in StubGenerator.TWEET_STUBS['futurecolors']:
            if 'in_reply_to_user_id' not in stub:
                self.assertEquals(tweets_context.popleft().text, stub['text'])

    def test_twitter_tag_with_no_retweets(self):
        output, context = self.render_template(
            template="""{% load twitter_tag %}{% get_tweets for "futurecolors" as tweets exclude "retweets" %}""")

        self.api.GetUserTimeline.assert_called_with(screen_name='futurecolors', include_rts=False, include_entities=True)
        self.assertEquals(len(context['tweets']), 3, 'Stub contains 4 tweets, including 1 retweet')

    def test_twitter_tag_with_no_replies_no_retweets(self):
        output, context = self.render_template(
            template="""{% load twitter_tag %}{% get_tweets for "futurecolors" as tweets exclude "retweets,replies" %}""")

        self.api.GetUserTimeline.assert_called_with(screen_name='futurecolors', include_rts=False, include_entities=True)
        self.assertEquals(len(context['tweets']), 2, 'Stub contains 4 tweets, including 1 reply & 1 retweet')

    def test_bad_syntax(self):
        self.assertRaises(TemplateSyntaxError, Template, """{% load twitter_tag %}{% get_tweets %}""")
        self.assertRaises(TemplateSyntaxError, Template, """{% load twitter_tag %}{% get_tweets as "tweets" %}""")

    @patch.object(settings, 'DEBUG', True)
    def test_exception_in_debug_mode(self):
        self.api.GetUserTimeline.side_effect = twitter.TwitterError

        template = Template("""{% load twitter_tag %}{% get_tweets for "twitter" as tweets %}""")
        self.assertRaises(twitter.TwitterError, template.render, Context())

    @patch.object(settings, 'DEBUG', False)
    def test_no_exception_in_production(self):
        self.api.GetUserTimeline.side_effect = twitter.TwitterError

        output, context = self.render_template(
            template="""{% load twitter_tag %}{% get_tweets for "twitter" as tweets %}""")
        self.assertEqual(output, '')
        self.assertEqual(context['tweets'], [])
