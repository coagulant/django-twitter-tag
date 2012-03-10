# -*- coding: utf-8 -*-
from __future__ import with_statement
import collections
import urllib2
from django.core.cache import cache
from django.template import Template, Context, TemplateSyntaxError
import twitter
from mock import patch
from unittest import TestCase
from twitter_tag.templatetags.twitter_tag import get_cache_key


TWEET_JSON = {'created_at': 'Mon Feb 27 20:53:48 +0000 2012',
 'favorited': False,
 'id': 174235806314139650,
 'retweet_count': 1,
 'retweeted': False,
 'retweeted_status': {'created_at': 'Mon Feb 27 20:18:52 +0000 2012',
  'favorited': False,
  'id': 174227015380111363,
  'in_reply_to_screen_name': 'futurecolors',
  'in_reply_to_status_id': 174225572497596416,
  'in_reply_to_user_id': 54171637,
  'retweet_count': 1,
  'retweeted': False,
  'urls': [twitter.Url(url='http://t.co/aVQRnBKP', expanded_url='http://travis-ci.com'),
           twitter.Url(url='http://t.co/7KgHV8iI', expanded_url='http://love.travis-ci.org')],
  'source': '<a href="http://itunes.apple.com/us/app/twitter/id409789998?mt=12" rel="nofollow">Twitter for Mac</a>',
  'text': u'@futurecolors \u0447\u0435\u0440\u0435\u0437 \u043d\u0435\u0441\u043a\u043e\u043b\u044c\u043a\u043e \u043c\u0435\u0441\u044f\u0446\u0435\u0432 \u0431\u0443\u0434\u0435\u0442 \u0438 \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430 \u043f\u0440\u0438\u0432\u0430\u0442\u043d\u044b\u0445 \u0440\u0435\u043f\u043e\u0437\u0438\u0442\u043e\u0440\u0438\u0435\u0432 (\u043d\u0430 http://t.co/aVQRnBKP). \u041f\u043e\u0434\u0440\u043e\u0431\u043d\u0435\u0435: http://t.co/7KgHV8iI',
  'truncated': False,
  'user': {'created_at': 'Tue Feb 15 08:34:44 +0000 2011',
   'description': u"Hi I'm Travis.\r\n\r\nI'm a distributed continuous integration service for the open source community \u2014 currently in early alpha, and I'm looking for your help!",
   'favourites_count': 3,
   'followers_count': 1736,
   'friends_count': 602,
   'id': 252481460,
   'lang': 'en',
   'listed_count': 73,
   'name': 'Travis CI',
   'profile_background_color': 'C0DEED',
   'profile_background_tile': False,
   'profile_image_url': 'http://a0.twimg.com/profile_images/1788260785/travis_normal.png',
   'profile_link_color': '0084B4',
   'profile_sidebar_fill_color': 'http://a0.twimg.com/images/themes/theme1/bg.png',
   'profile_text_color': '333333',
   'protected': False,
   'screen_name': 'travisci',
   'statuses_count': 1123,
   'url': 'http://travis-ci.org'}},
 'source': 'web',
 'text': u'RT @travisci: @futurecolors \u0447\u0435\u0440\u0435\u0437 \u043d\u0435\u0441\u043a\u043e\u043b\u044c\u043a\u043e \u043c\u0435\u0441\u044f\u0446\u0435\u0432 \u0431\u0443\u0434\u0435\u0442 \u0438 \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430 \u043f\u0440\u0438\u0432\u0430\u0442\u043d\u044b\u0445 \u0440\u0435\u043f\u043e\u0437\u0438\u0442\u043e\u0440\u0438\u0435\u0432 (\u043d\u0430 http://t.co/aVQRnBKP). \u041f\u043e\u0434\u0440\u043e\u0431\u043d\u0435\u0435: http: ...',
 'truncated': False,
 'urls': [twitter.Url(url='http://t.co/aVQRnBKP', expanded_url='http://travis-ci.com'),],
 'user': {'created_at': 'Mon Jul 06 10:27:52 +0000 2009',
  'description': u'\u041c\u044b \u0440\u0435\u0433\u0443\u043b\u044f\u0440\u043d\u043e \u043f\u0438\u0448\u0435\u043c \u043f\u0440\u043e \u043d\u0430\u0448\u0438 \u0434\u043e\u0441\u0442\u0438\u0436\u0435\u043d\u0438\u044f \u0432 \u0438\u043d\u0442\u0435\u0440\u043d\u0435\u0442\u0430\u0445 \u0438 \u043f\u0440\u043e \u043d\u043e\u0432\u043e\u0441\u0442\u0438 \u0432\u0435\u0431-\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0438.',
  'favourites_count': 10,
  'followers_count': 202,
  'friends_count': 75,
  'id': 54171637,
  'lang': 'ru',
  'listed_count': 14,
  'location': 'Moscow, Russia',
  'name': u'\u0421\u0442\u0443\u0434\u0438\u044f Future Colors',
  'profile_background_color': 'ffffff',
  'profile_background_tile': False,
  'profile_image_url': 'http://a0.twimg.com/profile_images/299739915/fc_twitter_normal.png',
  'profile_link_color': '0084B4',
  'profile_sidebar_fill_color': 'http://a0.twimg.com/images/themes/theme1/bg.png',
  'profile_text_color': '333333',
  'protected': False,
  'screen_name': 'futurecolors',
  'statuses_count': 597,
  'time_zone': 'Moscow',
  'url': 'http://futurecolors.ru',
  'utc_offset': 14400}}


class StubGenerator(object):
    TWEET_STUBS = {'jresig':
                       [{'text': "This is not John Resig - you should be following @jeresig instead!",
                        'html': "This is not John Resig - you should be following <a href=\"http://twitter.com/jeresig\">@jeresig</a> instead!"}],
                   'futurecolors':
                       [{'text': u"JetBrains радуют новыми фичами и апдейтами старых. Пост из блога #pycharm про дебаг шаблонов джанги в их IDE http://ht.ly/6viu3"},
                        {'text': u"На новых проектах будем использовать django-jenkins и django-any http://t.co/FjhHpdwV http://t.co/Hig8Hsjg Очень полезные штуки."},
                        {'text': u"@goshakkk Переход на руби был связан именно с отсутствием поддержки py3k? :)",
                         'in_reply_to_user_id': 61236914},
                        {'text': u"Наконец-то начались какие-то попытки портировать #Django на #python3 http://t.co/XkftDsQH",
                         'retweeted': True},
                       ],
                  }

    @classmethod
    def get_timeline(cls, screen_name, include_rts, **kwargs):
        user = cls.get_user(screen_name=screen_name)
        tweets = []
        for stub in cls.TWEET_STUBS[screen_name]:
            if not include_rts and stub.get('retweeted', False):
                continue
            data = stub.copy()
            html = data.pop('html', '')
            tweet = cls.get_status(user=user, **data)
            tweet.html = html
            tweets.append(tweet)
        return tweets

    @classmethod
    def get_user(cls, screen_name, **kwargs):
        return twitter.User(screen_name=screen_name, **kwargs)

    @classmethod
    def get_status(cls, **kwargs):
        return twitter.Status(**kwargs)


class BaseTwitterTagTestCase(TestCase):
    def setUp(self):
        self.patcher = patch('twitter.Api')
        mock = self.patcher.start()
        self.api = mock.return_value
        self.api.GetUserTimeline.side_effect = StubGenerator.get_timeline

    def tearDown(self):
        self.patcher.stop()

    def render_template(self, template):
        context = Context()
        template = Template(template)
        output = template.render(context)
        return output, context


class ExtendedFeaturesTweet(BaseTwitterTagTestCase):
    def setUp(self):
        self.patcher = patch('twitter.Api')
        mock = self.patcher.start()
        self.api = mock.return_value
        self.api.GetUserTimeline.return_value = [twitter.Status(**TWEET_JSON)]

    def test_trimmed_tweet(self):
        output, context = self.render_template(template="""{% load twitter_tag %}{% get_tweets for "futurecolors" as tweets %}""")
        print context['tweets'][0].html
        self.assertTrue(context['tweets'][0].text.endswith(u'...'))
        self.assertFalse(context['tweets'][0].html.endswith(u'...'))
        self.assertTrue(context['tweets'][0].html.startswith(u'RT <a href="http://twitter.com/futurecolors">@futurecolors</a>: '))

    def test_url_is_expanded(self):
        output, context = self.render_template(template="""{% load twitter_tag %}{% get_tweets for "futurecolors" as tweets %}""")
        self.assertTrue(u'http://travis-ci.com' in context['tweets'][0].html)
        self.assertTrue(u'http://love.travis-ci.org' in context['tweets'][0].html)


class TwitterTagTestCase(BaseTwitterTagTestCase):
    def test_twitter_tag_simple_mock(self):

        output, context = self.render_template(template="""{% load twitter_tag %}{% get_tweets for "jresig" as tweets %}""")

        self.api.GetUserTimeline.assert_called_with(screen_name='jresig', include_rts=True, include_entities=True)
        self.assertEquals(len(context['tweets']), 1, 'jresig account has only one tweet')
        self.assertEquals(output, '')
        self.assertEquals(context['tweets'][0].text, StubGenerator.TWEET_STUBS['jresig'][0]['text'], 'one and only tweet text')
        self.assertEquals(context['tweets'][0].html, StubGenerator.TWEET_STUBS['jresig'][0]['html'], 'corresponding html for templates')

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


class ExceptionHandlingTestCase(BaseTwitterTagTestCase):

    logger_name = 'twitter_tag.templatetags.twitter_tag'

    def test_bad_syntax(self):
        self.assertRaises(TemplateSyntaxError, Template, """{% load twitter_tag %}{% get_tweets %}""")
        self.assertRaises(TemplateSyntaxError, Template, """{% load twitter_tag %}{% get_tweets as "tweets" %}""")

    @patch('logging.getLogger')
    def test_exception_is_not_propagated_but_logged(self, logging_mock):
        exception_message = "Capacity Error"
        self.api.GetUserTimeline.side_effect = twitter.TwitterError(exception_message)

        output, context = self.render_template(
            template="""{% load twitter_tag %}{% get_tweets for "twitter" as tweets %}""")
        self.assertEqual(output, '')
        self.assertEqual(context['tweets'], [])

        logging_mock.assert_called_with(self.logger_name)
        logging_mock.return_value.error.assert_called_with(exception_message)

    @patch('logging.getLogger')
    def test_urlerror_exception(self, logging_mock):
        exception_message = "Twitter.com is not resolving"
        self.api.GetUserTimeline.side_effect = urllib2.URLError(exception_message)
        
        output, context = self.render_template(
                template="""{% load twitter_tag %}{% get_tweets for "twitter" as tweets %}""")
        self.assertEqual(output, '')
        self.assertEqual(context['tweets'], [])

        logging_mock.assert_called_with(self.logger_name)
        logging_mock.return_value.error.assert_called_with('<urlopen error %s>' % exception_message)

    @patch('logging.getLogger')
    def test_get_from_cache_when_twitter_api_fails(self, logging_mock):
        exception_message = 'Technical Error'
        # it should be ok by now
        self.render_template(
            template="""{% load twitter_tag %}{% get_tweets for "jresig" as tweets %}""")
        cache_key = get_cache_key('jresig', 'tweets')
        self.assertEqual(len(cache.get(cache_key)), len(StubGenerator.TWEET_STUBS['jresig']))
        self.assertEqual(cache.get(cache_key)[0].text, StubGenerator.TWEET_STUBS['jresig'][0]['text'])

        # when twitter api fails, should use cache
        self.api.GetUserTimeline.side_effect = twitter.TwitterError(exception_message)
        output, context = self.render_template(
            template="""{% load twitter_tag %}{% get_tweets for "jresig" as tweets %}""")
        self.assertEquals(len(context['tweets']), 1, 'jresig account has only one tweet')
        self.assertEqual(context['tweets'][0].text, StubGenerator.TWEET_STUBS['jresig'][0]['text'])
        logging_mock.assert_called_with(self.logger_name)
        logging_mock.return_value.error.assert_called_with(exception_message)
