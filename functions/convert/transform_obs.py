# -*- coding: utf-8 -*-

# Transforms OBS from md to html

from __future__ import print_function, unicode_literals

import codecs
import os
import re
import shutil
import tempfile
import markdown
import string

from glob import glob
from general_tools.file_utils import unzip, make_dir, write_file
from general_tools.print_utils import print_error
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
            file_to_download = self.source_url
            filename = self.source_url.rpartition('/')[2]
            downloaded_file = os.path.join(self.downloadDir, filename)
            try:
                print('Downloading {0}...'.format(file_to_download), end=' ')
                if not os.path.isfile(downloaded_file):
                    download_file(file_to_download, downloaded_file)
            finally:
                print('finished.')

            # unzip the archive
            try:
                print('Unzipping...'.format(downloaded_file), end=' ')
                unzip(downloaded_file, self.filesDir)
            finally:
                print('finished.')

            # create output directory
            make_dir(self.outputDir)

            # read the markdown files and output html files
            try:
                print('Processing the OBS markdown files')

                files_to_process = sorted(glob(os.path.join(self.filesDir, '*.md')))

                current_dir = os.path.dirname(os.path.realpath(__file__))

                with open(os.path.join(current_dir, 'template.html')) as template_file:
                    html_template = string.Template(template_file.read())

                complete_html = ''
                for filename in files_to_process:
                    # read the markdown file
                    with codecs.open(filename, 'r', 'utf-8-sig') as md_file:
                        md = md_file.read()
                        html = markdown.markdown(md)
                        complete_html += html
                        html = html_template.substitute(content=html)
                        html_filename = os.path.splitext(os.path.basename(filename))[0]+".html"
                        write_file(os.path.join(self.outputDir, html_filename), html)

                complete_html = html_template.substitute(content=complete_html)
                write_file(os.path.join(self.outputDir, 'obs.html'), complete_html)

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
