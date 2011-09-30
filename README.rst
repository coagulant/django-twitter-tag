Django Twitter Tag
==================

A django template tag to display user's recent tweets.

You can limit number of tweets, filter out replies and retweets.
Since the app exposes python-twitter_ ``Status`` model to template context,
you can also access any tweet attributes or methods for your needs.
You don't need to parse tweets to make urls, hashtags or twitter usernames clickable, it has been done for you already.
Just use tweet's ``html`` attrubute (see example below).

.. _python-twitter: http://python-twitter.googlecode.com/hg/doc/twitter.html

Installation
------------

Recommended way to install is pip::

  pip install django-twitter-tag


Usage
-----

* Add ``twitter_tag`` to ``INSTALLED_APPS`` in settings.py::

    INSTALLED_APPS = (...
                      'twitter_tag',
                      ...
                     )

* Load tag in your template like this::

    {% load twitter_tag %}


* Get user's (futurecolors in example) most recent tweets and store them in ``tweets`` variable::

    {% get_tweets for "futurecolors" as tweets %}


* Now you have a list of tweets in your template context, which you can iterate over like this::

    <ul>
    {% for tweet in tweets %}
        <li>{{ tweet.html|safe }}</li>
    {% endfor %}
    </ul>


Examples
--------

You can specify number of tweets to get::

    {% get_tweets for "futurecolors" as tweets exclude "replies" limit 10 %}


To filter out tweet replies (that start with @ char)::

    {% get_tweets for "futurecolors" as tweets exclude "replies" limit 10 %}


To ignore native retweets::

    {% get_tweets for "futurecolors" as tweets exclude "retweets" %}
    

Caching
-------

It's strongly advised to use template caching framework to reduce the amount of twitter API calls
and avoid reaching possible request limit::

    {% load twitter_tag cache %}
    {% cache 3600 my_tweets %}
    {% get_tweets for "futurecolors" as tweets exclude "retweets" %}
    ...
    {% endcache %}


Extra
-----

Tweet's properties
~~~~~~~~~~~~~~~~~~

get_tweets holds a list of ``Status`` objects, which represet single user tweet.
According to python-twitter_ API, every status has following attributes, availiable in templates::

  status.created_at
  status.created_at_in_seconds
  status.favorited
  status.in_reply_to_screen_name
  status.in_reply_to_user_id
  status.in_reply_to_status_id
  status.truncated
  status.source
  status.id
  status.text
  status.location
  status.relative_created_at
  status.user
  status.urls
  status.user_mentions
  status.hashtags


Tweet's html
~~~~~~~~~~~~

Tweet also has extra ``status.html`` property, which contains tweet, formatted for html output
with all needed links.


Exception handling
~~~~~~~~~~~~~~~~~~

Any Twitter API exceptions like 'Over capacity' are silenced and logged.
