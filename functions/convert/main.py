# -*- coding: utf-8 -*-

# Method for converting MD files to HTML

from __future__ import print_function, unicode_literals

import codecs
import os
import re
import shutil
import tempfile
from contextlib import closing
import markdown
import boto3
import datetime

from glob import glob
from general_tools.file_utils import unzip, add_file_to_zip, make_dir, write_file
from general_tools.print_utils import print_error, print_ok
from general_tools.url_utils import download_file

class TransformOBS(object):

    dirRe = re.compile(r'(<div\s.*?class=".*?obs-content.*?">).*?(</div>)', re.UNICODE + re.DOTALL)

    def __init__(self, source_url, outputDir, options):
        self.source_url = source_url
        self.outputDir = outputDir
        self.options = options

        self.downloadDir = tempfile.mkdtemp(prefix='download_')
        self.filesDir = tempfile.mkdtemp(prefix='files_')
        self.errors = []

    def close(self):
        # delete temp files
        if os.path.isdir(self.downloadDir):
            shutil.rmtree(self.downloadDir, ignore_errors=True)
        if os.path.isdir(self.filesDir):
            shutil.rmtree(self.filesDir, ignore_errors=True)

    def run(self):
        try:
            # download the archive
            fileToDownload = self.source_url
            filename = self.source_url.rpartition('/')[2]
            downloadedFile = os.path.join(self.downloadDir, filename)
            try:
                print('Downloading {0}...'.format(fileToDownload), end=' ')
                if not os.path.isfile(downloadedFile):
                    download_file(fileToDownload, downloadedFile)
            finally:
                print('finished.')

            # unzip the archive
            try:
                print('Unzipping...'.format(downloadedFile), end=' ')
                unzip(downloadedFile, self.filesDir)
            finally:
                print('finished.')

            # create output directory
            make_dir(self.outputDir)

            # read the markdown files and output html files
            try:
                print('Processing the OBS markdown files')

                files_to_process = sorted(glob(os.path.join(self.filesDir, '*.md')))

                currentDir = os.path.dirname(os.path.realpath(__file__))
                with codecs.open(os.path.join(currentDir, 'template.html'), 'r', 'utf-8-sig') as html_file:
                    html_template = html_file.read()

                completeHtml = ''
                for filename in files_to_process:
                   # read the markdown file
                    with codecs.open(filename, 'r', 'utf-8-sig') as md_file:
                        md = md_file.read()
                        html = markdown.markdown(md)
                        completeHtml += html
                        html = TransformOBS.dirRe.sub(r'\1\n' + html + r'\n\2', html_template)
                        htmlFileName = os.path.splitext(os.path.basename(filename))[0]+".html"
                        write_file(os.path.join(self.outputDir, htmlFileName), html)

                completeHtml = TransformOBS.dirRe.sub(r'\1\n' + completeHtml + r'\n\2', html_template)
                write_file(os.path.join(self.outputDir, 'obs.html'), completeHtml)

            except IOError as ioe:
                print_error('{0}: {1}'.format(ioe.strerror, ioe.filename))
                self.errors.append(ioe)

            except Exception as e:
                print_error(e.message)
                self.errors.append(e)

            finally:
                print('finished.')

        except Exception as e:
            print_error(e.message)
            self.errors.append(e)


def handle(event, context):
    if not 'data' in event:
        raise Exception('"data" was not in payload')
    data = event['data']

    if not 'job' in data:
        raise Exception('"job" was not in payload')
    job = data['job']

    if not 'source' in job:
        raise Exception('"source" was not in "job"')
    source = job['source']

    if not 'resource_type' in job:
        raise Exception ('"resource_type" was not in "job"')
    resource = job['resource_type']

    if not 'cdn_bucket' in data:
        raise Exception('"cdn_bucket" was not payload')
    cdnBucket = data['cdn_bucket']

    if not 'cdn_file' in data:
        raise Exception('"cdn_file" was not in payload')
    cdnFile = data['cdn_file']

    print('source: ' + source)
    print('cdnBucket: ' + cdnBucket)
    print('cdnFile: ' + cdnFile)

    options = {
        'line_spacing': '120%'
    }

    if 'options' in job:
        options.update(job['options'])

    outputDir = os.path.join(tempfile.gettempdir(), context.aws_request_id)

    if resource == 'obs':
        # call with closing to be sure the temp files get cleaned up
        with closing(TransformOBS(source, outputDir, options)) as tx:
            tx.run()
    else:
        raise Exception('Resource "{0}" not supported'.format(resource))

    zipFile = os.path.join(tempfile.gettempdir(), context.aws_request_id+'.zip')
    for filename in glob(os.path.join(outputDir, '*.html')):
        add_file_to_zip(zipFile, filename, os.path.basename(filename))

    print("Uploading {0} to {1}/{2}".format(zipFile, cdnBucket, cdnFile))
    s3Client = boto3.client('s3')
    s3Client.upload_file(zipFile, cdnBucket, cdnFile)

    return {
        'success': True,
        'output': job['output'],
    }
