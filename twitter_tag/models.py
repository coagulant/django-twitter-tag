from appconf import AppConf


class TwitterConf(AppConf):
    OAUTH_TOKEN = None
    OAUTH_SECRET = None
    CONSUMER_KEY = None
    CONSUMER_SECRET = None

    class Meta:
        prefix = 'twitter'
        required = ['OAUTH_TOKEN', 'OAUTH_SECRET', 'CONSUMER_KEY', 'CONSUMER_SECRET']