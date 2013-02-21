# coding: utf-8
import io
import os
from django.template import Context, Template


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
    return dict((k, v) for k, v in query.items() if k not in oauth_keys)


def get_json(somefile):
    with io.open(os.path.join('tests', 'json', somefile), mode='rb') as f:
        return f.read()