import json
import httplib
import os

from subprocess import call

call("pip install elasticsearch",shell=True)
call("pip install slackclient",shell=True)
try:
    from six.moves.urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

import requests

from elasticsearch import Elasticsearch
from st2actions.runners.pythonrunner import Action

__all__ = [
    'PostMessageAction'
]


class PostMessageAction(Action):

    def run(self):
        es = Elasticsearch()
        res = es.search(index="",doc_type="",body={"query": {"match": {"message": "VLAN"}}})

        for doc in res['hits']['hits']:
            print(doc['_id'],doc['_source']['message'])

    def run(self, message=None, username=None, icon_emoji=None, channel=None,
            disable_formatting=False):


        config = self.config['post_message_action']
        username = username if username else config['username']
        icon_emoji = icon_emoji if icon_emoji else config.get('icon_emoji', None)
        channel = channel if channel else config.get('channel', None)



        message = message if message else config.get('message',None)

        headers = {}
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        body = {
            'username': username,
            'icon_emoji': icon_emoji,
            'text': message
        }

        if channel:
            body['channel'] = channel

        if disable_formatting:
            body['parse'] = 'none'

        data = {'payload': json.dumps(body)}
        data = urlencode(data)
        response = requests.post(url=config['webhook_url'],
                                 headers=headers, data=data)

        if response.status_code == httplib.OK:
            self.logger.info('Message successfully posted')
        else:
            failure_reason = ('Failed to post message: %s (status code: %s)' %
                              (response.text, response.status_code))
            self.logger.exception(failure_reason)
            raise Exception(failure_reason)

        return True
