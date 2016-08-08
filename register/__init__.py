from __future__ import print_function, unicode_literals
import requests


def register():
    post_url = 'https://api.door43.org/tx/module'
    post_data = {'name': 'md2html',
                 'version': '1',
                 'type': 'conversion',
                 'resource_types': ['obs'],
                 'input_format': ['md'],
                 'output_format': ['html'],
                 'options': [],
                 'private_links': [],
                 'public_links': []}

    response = requests.post(post_url, data=post_data)

    if response.ok:
        print('Registered successfully.')


if __name__ == '__main__':
    register()
