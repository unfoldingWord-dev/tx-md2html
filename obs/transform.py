from __future__ import print_function, unicode_literals
import argparse
import codecs
import inspect
import os
import re
import shutil
import sys
import tempfile
from contextlib import closing
import markdown
from general_tools.file_utils import unzip, load_json_object, make_dir, write_file
from general_tools.print_utils import print_error, print_warning, print_ok
from general_tools.url_utils import join_url_parts, download_file


class TransformOBS(object):

    dir_re = re.compile(r'(<div\s.*?class=".*?obs-content.*?">).*?(</div>)', re.UNICODE + re.DOTALL)

    def __init__(self, source_repo_url, output_directory):

        self.temp_dir = tempfile.mkdtemp(prefix='txOBS_')
        self.errors = []
        self.source_repo_url = source_repo_url
        self.output_directory = output_directory

    def close(self):
        # delete temp files
        if os.path.isdir(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def run(self):

        if 'git.door43.org' not in self.source_repo_url:
            print_warning('Currently only git.door43.org repositories are supported.')
            sys.exit(0)

        try:
            # clean up the git repo url
            if self.source_repo_url[-4:] == '.git':
                self.source_repo_url = self.source_repo_url[:-4]

            if self.source_repo_url[-1:] == '/':
                self.source_repo_url = self.source_repo_url[:-1]

            # download the archive
            file_to_download = join_url_parts(self.source_repo_url, 'archive/master.zip')
            repo_dir = self.source_repo_url.rpartition('/')[2]
            downloaded_file = os.path.join(self.temp_dir, repo_dir + '.zip')
            try:
                print('Downloading {0}...'.format(file_to_download), end=' ')
                if not os.path.isfile(downloaded_file):
                    download_file(file_to_download, downloaded_file)
            finally:
                print('finished.')

            # unzip the archive
            try:
                print('Unzipping...'.format(downloaded_file), end=' ')
                unzip(downloaded_file, self.temp_dir)
            finally:
                print('finished.')

            # get the manifest
            try:
                print('Reading the manifest...', end=' ')
                manifest = load_json_object(os.path.join(self.temp_dir, 'manifest.json'))
            finally:
                print('finished.')

            # create output directory
            make_dir(self.output_directory)

            # read the markdown files and output html files
            try:
                print('Processing the OBS markdown files')
                files_to_process = []
                for i in range(1, 51):
                    files_to_process.append(str(i).zfill(2) + '.md')

                current_dir = os.path.dirname(inspect.stack()[0][1])
                with codecs.open(os.path.join(current_dir, 'template.html'), 'r', 'utf-8-sig') as html_file:
                    html_template = html_file.read()

                for file_to_process in files_to_process:

                    # read the markdown file
                    file_name = os.path.join(self.temp_dir, repo_dir, 'content', file_to_process)
                    with codecs.open(file_name, 'r', 'utf-8-sig') as md_file:
                        md = md_file.read()

                    html = markdown.markdown(md)
                    html = TransformOBS.dir_re.sub(r'\1\n' + html + r'\n\2', html_template)
                    write_file(os.path.join(self.output_directory, file_to_process.replace('.md', '.html')), html)

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


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-r', '--gitrepo', dest='gitrepo', default=False,
                        required=True, help='Git repository where the source can be found.')
    parser.add_argument('-o', '--outdir', dest='outdir', default=False,
                        required=True, help='The output directory for markdown files.')

    args = parser.parse_args(sys.argv[1:])

    # call with closing to be sure the temp files get cleaned up
    with closing(TransformOBS(args.gitrepo, args.outdir)) as tx:
        tx.run()

    print_ok('ALL FINISHED: ', 'Please check the output directory.')
