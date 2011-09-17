from django.template import Template, Context
from django.template.base import TemplateSyntaxError
from django.test import TestCase


class TwitterTagTestCase(TestCase):
    
    def test_twitter_tag_simple(self):
        context = Context()
        template = Template( """{% load twitter_tags %}{% get_tweets_new for "jresig" as tweets %}""")
        template.render(context)

        self.assertEquals(len(context['tweets']), 1)
        self.assertEquals(context['tweets'][0]['text'], 'This is not John Resig - you should be following @jeresig instead!')
        self.assertEquals(context['tweets'][0]['html'], 'This is not John Resig - you should be following <a href="http://twitter.com/jeresig">@jeresig</a> instead!')


    def test_twitter_tag_limit(self):
        context = Context()
        template = Template( """{% load twitter_tags %}{% get_tweets_new for "futurecolors" as tweets limit 2 %}""")
        template.render(context)

        self.assertEquals(len(context['tweets']), 2)


    def test_twitter_tag_with_replies(self):
        context = Context()
        template = Template( """{% load twitter_tags %}{% get_tweets_new for "futurecolors" as tweets with replies limit 2 %}""")
        template.render(context)

        self.assertEquals(len(context['tweets']), 2)

        
    def test_bad_syntax(self):
        self.assertRaises(TemplateSyntaxError, Template, """{% load twitter_tags %}{% get_tweets_new %}""")


