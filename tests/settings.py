import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

SITE_ID = 1
PROJECT_APPS = ('twitter_tag',)
INSTALLED_APPS = ( 'django.contrib.auth',
                   'django.contrib.contenttypes',
                   'django.contrib.sessions',
                   'django.contrib.sites',
                   'django.contrib.admin',
                   'django_jenkins',) + PROJECT_APPS
DATABASE_ENGINE = 'sqlite3'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.%s' % DATABASE_ENGINE,
        }
}
ROOT_URLCONF = 'tests.urls'
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
