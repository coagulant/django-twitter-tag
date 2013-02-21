from __future__ import unicode_literals
from appconf import AppConf


class TwitterConf(AppConf):
    class Meta:
        prefix = 'twitter'
        required = ['OAUTH_TOKEN', 'OAUTH_SECRET', 'CONSUMER_KEY', 'CONSUMER_SECRET']