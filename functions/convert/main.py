# -*- coding: utf-8 -*-

# Method for converting MD files to HTML

from __future__ import print_function, unicode_literals

import os
import tempfile
import boto3

import transform_obs

from glob import glob
from contextlib import closing

from general_tools.file_utils import add_file_to_zip

def log_message(log, message):
    print('{0}: {1}'.format('tx-md2html_convert', message))
    log.append('{0}: {1}'.format('tx-md2html_convert', message))


def error_message(errors, message):
    print('{0}: {1}'.format('tx-md2html_convert', message))
    errors.append('{0}: {1}'.format('tx-md2html_convert', message))


def warning_message(warnings, message):
    print('{0}: {1}'.format('tx-md2html_convert', message))
    warnings.append('{0}: {1}'.format('tx-md2html_convert', message))


def handle(event, context):
    log = []
    errors = []
    warnings = []

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
    
    if 'cdn_bucket' not in job:
        raise Exception('"cdn_bucket" was not in "job"')
    cdn_bucket = job['cdn_bucket']
    
    if 'cdn_file' not in job:
        raise Exception('"cdn_file" was not in "job')
    cdn_file = job['cdn_file']
    
    print('source: ' + source)
    print('cdn_bucket: ' + cdn_bucket)
    print('cdn_file: ' + cdn_file)
    
    options = {
        'line_spacing': '120%'
    }
    
    if 'options' in job:
        options.update(job['options'])
    
    output_dir = os.path.join(tempfile.gettempdir(), context.aws_request_id)

    try:
        if resource == 'obs':
            # call with closing to be sure the temp files get cleaned up
            with closing(transform_obs.TransformOBS(source, output_dir, options)) as obs:
                obs.run()
                log.extend(obs.log)
                errors.extend(obs.errors)
                warnings.extend(obs.warnings)
        # --- Add other resources here when implemented ---
        else:
            raise Exception('Resource "{0}" not currently supported'.format(resource))
        
        zip_file = os.path.join(tempfile.gettempdir(), context.aws_request_id+'.zip')
        for filename in glob(os.path.join(output_dir, '*.html')):
            add_file_to_zip(zip_file, filename, os.path.basename(filename))
        
        log_message(log, "Uploading {0} to {1}/{2}".format(os.path.basename(zip_file), cdn_bucket, cdn_file))
        s3_client = boto3.client('s3')
        s3_client.upload_file(zip_file, cdn_bucket, cdn_file)
        log_message(log, "Upload was successful.")
    except Exception as e:
        error_message(errors, e.message)

    return {
        'log': log,
        'errors': errors,
        'warnings': warnings,
        'success': (len(errors) > 0)
    }