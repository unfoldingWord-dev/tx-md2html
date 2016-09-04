# -*- coding: utf-8 -*-

# Method for  registering this module

from __future__ import print_function, unicode_literals
import requests
import json

def handle(event, ctx):
    if not 'tx_manager_url' in event:
        raise Exception("'text_manager_url' not in payload")

    post_url = event['tx_manager_url']+'/module'
    post_data = {'name': 'tx-md2html_convert',
                 'version': '1',
                 'type': 'conversion',
                 'resource_types': ['obs'],
                 'input_format': ['md'],
                 'output_format': ['html'],
                 'options': [],
                 'private_links': [],
                 'public_links': []}

    response = requests.post(post_url, data=post_data, headers={'content-type': 'application/json'})
    return json.loads(response.text)
