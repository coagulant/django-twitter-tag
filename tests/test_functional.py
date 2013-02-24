# coding: utf-8
# from __future__ import unicode_literals
# import os
# import mock
# from django.conf import settings
# from nose.plugins.attrib import attr
# from nose.tools import nottest
# from .utils import render_template
#
#
# @nottest
# @attr('functional')
# @mock.patch.multiple(settings, TWITTER_OAUTH_TOKEN=os.environ.get('OAUTH_TOKEN'),
#                                TWITTER_OAUTH_SECRET=os.environ.get('OAUTH_SECRET'),
#                                TWITTER_CONSUMER_KEY=os.environ.get('CONSUMER_KEY'),
#                                TWITTER_CONSUMER_SECRET=os.environ.get('CONSUMER_SECRET'), create=True)
# def test_func():
#     o, c = render_template("""{% search_tweets for "питон" as tweets %}""")
#     for t in c['tweets']:
#         assert 'питон' in t['html'].lower()