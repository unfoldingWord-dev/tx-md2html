# test Transform OBS from md to html using internal files

from __future__ import print_function, unicode_literals

import codecs
import os
import shutil
import tempfile
import markdown
import string

from glob import glob
from shutil import copyfile
from general_tools.file_utils import unzip, make_dir, write_file
from general_tools.url_utils import download_file
from door43_tools.obs_handler import OBSInspection


class TransformOBS(object):

    def __init__(self, source_url, output_dir, options):
        self.source_url = source_url
        self.output_dir = output_dir
        self.options = options
        self.download_dir = tempfile.mkdtemp(prefix='download_')
        self.files_dir = tempfile.mkdtemp(prefix='files_')
        self.log = []
        self.warnings = []
        self.errors = []
        self.failed = False;

    def log_message(self, message):
        print(message)
        self.log.append(message)

    def error_message(self, message):
        print(message)
        self.errors.append(message)

    def warning_message(self, message):
        print(message)
        self.warnings.append(message)

    def close(self):
        # delete temp files
        if os.path.isdir(self.download_dir):
            shutil.rmtree(self.download_dir, ignore_errors=True)
        if os.path.isdir(self.files_dir):
            shutil.rmtree(self.files_dir, ignore_errors=True)

    def run(self, internal_file=None): # optionally use internal file (useful for testing)
        if not internal_file:
            # download the archive
            file_to_download = self.source_url
            filename = self.source_url.rpartition('/')[2]
            downloaded_file = os.path.join(self.download_dir, filename)
            self.log_message('Downloading {0}...'.format(file_to_download))
            if not os.path.isfile(downloaded_file):
                try:
                    download_file(file_to_download, downloaded_file)
                finally:
                    if not os.path.isfile(downloaded_file):
                        raise Exception("Failed to download {0}".format(file_to_download))
                    else:
                        self.log_message('Download successful.')
        else:
            downloaded_file = internal_file

        # unzip the archive
        self.log_message('Unzipping {0}...'.format(downloaded_file))
        unzip(downloaded_file, self.files_dir)
        self.log_message('Unzip successful.')

        # create output directory
        make_dir(self.output_dir)

        # read the markdown files and output html files
        self.log_message('Processing the OBS markdown files')

        files = sorted(glob(os.path.join(self.files_dir, '*')))

        current_dir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(current_dir, 'obs-template.html')) as template_file:
            html_template = string.Template(template_file.read())

        complete_html = ''
        for filename in files:
            if filename.endswith('.md'):
                # read the markdown file
                with codecs.open(filename, 'r', 'utf-8-sig') as md_file:
                    md = md_file.read()
                html = markdown.markdown(md)
                complete_html += html
                html = html_template.safe_substitute(content=html)
                base_name = os.path.splitext(os.path.basename(filename))[0]
                html_filename = base_name + ".html"
                output_file = os.path.join(self.output_dir, html_filename)
                write_file(output_file, html)
                self.log_message('Converted {0} to {1}.'.format(os.path.basename(filename), os.path.basename(html_filename)))

                # Do the OBS inspection
                inspector = OBSInspection(output_file) # this now operates on a single file instead of folder
                try:
                    inspector.run()
                except Exception as e:
                    self.warning_message('Chapter {0}: failed to run OBS inspector: {1}'.format(base_name, e.message))

                for warning in inspector.warnings:
                    self.warning_message(warning)
                for error in inspector.errors:
                    self.error_message(error)
        else:
            # copy files that are not md files
            try:
                output_file = os.path.join(self.output_dir, filename[len(self.files_dir)+1:])
                if not os.path.exists(output_file):
                    if not os.path.exists(os.path.dirname(output_file)):
                        os.makedirs(os.path.dirname(output_file))
                    copyfile(filename, output_file)
            except Exception:
                pass

        complete_html = html_template.safe_substitute(content=complete_html)
        write_file(os.path.join(self.output_dir, 'all.html'), complete_html)

        self.log_message('Made one HTML of all stories in all.html.')
        self.log_message('Finished processing Markdown files.')

