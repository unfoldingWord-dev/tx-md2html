# -*- coding: utf-8 -*-

# Method for converting MD files to HTML

from __future__ import print_function, unicode_literals

import os
import tempfile
from contextlib import closing
import boto3
import transform_obs

from glob import glob
from general_tools.file_utils import add_file_to_zip


def handle(event, context):
    if 'data' not in event:
        raise Exception('"data" was not in payload')
    data = event['data']

    if 'job' not in data:
        raise Exception('"job" was not in payload')
    job = data['job']

    if 'source' not in job:
        raise Exception('"source" was not in "job"')
    source = job['source']

    if 'resource_type' not in job:
        raise Exception ('"resource_type" was not in "job"')
    resource = job['resource_type']

    if 'cdn_bucket' not in data:
        raise Exception('"cdn_bucket" was not payload')
    cdn_bucket = data['cdn_bucket']

    if 'cdn_file' not in data:
        raise Exception('"cdn_file" was not in payload')
    cdn_file = data['cdn_file']

    print('source: ' + source)
    print('cdn_bucket: ' + cdn_bucket)
    print('cdn_file: ' + cdn_file)

    options = {
        'line_spacing': '120%'
    }

    if 'options' in job:
        options.update(job['options'])

    output_dir = os.path.join(tempfile.gettempdir(), context.aws_request_id)

    if resource == 'obs':
        # call with closing to be sure the temp files get cleaned up
        with closing(transform_obs.TransformOBS(source, output_dir, options)) as obs:
            obs.run()
    # --- Add other resources here when implemented ---
    else:
        raise Exception('Resource "{0}" not supported'.format(resource))

    zip_file = os.path.join(tempfile.gettempdir(), context.aws_request_id+'.zip')
    for filename in glob(os.path.join(output_dir, '*.html')):
        add_file_to_zip(zip_file, filename, os.path.basename(filename))

    print("Uploading {0} to {1}/{2}".format(zip_file, cdn_bucket, cdn_file))
    s3_client = boto3.client('s3')
    s3_client.upload_file(zip_file, cdn_bucket, cdn_file)

    return {
        'success': True,
        'output': job['output'],
    }
