# test Transform OBS from md to html using external url

from __future__ import print_function, unicode_literals
import os
import shutil
import tempfile
from contextlib import closing
import unittest
from functions.convert.transform_obs import TransformOBS

from general_tools.file_utils import unzip, add_contents_to_zip, add_file_to_zip
from door43_tools.preprocessors import TsObsMarkdownPreprocessor
from door43_tools.manifest_handler import Manifest, MetaData


class TestTransformOBS(unittest.TestCase):

    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')

    def setUp(self):
        """
        Runs before each test
        """
        self.out_dir = ''
        self.temp_dir = ""
        self.temp_dir2 = ""

    def tearDown(self):
        """
        Runs after each test
        """
        # delete temp files
        if os.path.isdir(self.out_dir):
            shutil.rmtree(self.out_dir, ignore_errors=True)
        if os.path.isdir(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        if os.path.isdir(self.temp_dir2):
            shutil.rmtree(self.temp_dir2, ignore_errors=True)

    @classmethod
    def setUpClass(cls):
        """
        Called before tests in this class are run
        """
        pass

    @classmethod
    def tearDownClass(cls):
        """
        Called after tests in this class are run
        """
        pass

    def test_close(self):
        """
        This tests that the temp directories are deleted when the class is closed
        """

        with closing(TransformOBS('', '', True)) as tx:
            download_dir = tx.download_dir
            files_dir = tx.files_dir

            # verify the directories are present
            self.assertTrue(os.path.isdir(download_dir))
            self.assertTrue(os.path.isdir(files_dir))

        # now they should have been deleted
        self.assertFalse(os.path.isdir(download_dir))
        self.assertFalse(os.path.isdir(files_dir))

    def test_completeMD(self):
        """
        Runs the converter and verifies the output
        """

        # given
        file_name = 'markdown_sources/aab_obs_text_obs'
        repo_name = 'aab_obs_text_obs'
        expected_warnings = 0
        expected_errors= 0
        zip_filepath = self.packageFiles(repo_name, file_name)

        # when
        tx = self.doTransformObs(zip_filepath)# verify the output

        #then
        self.verifyTransform(expected_errors, expected_warnings, tx)


    def test_missing_chapterMD(self):
        """
        Runs the converter and verifies the output
        """

        # given
        file_name = 'markdown_sources/aab_obs_text_obs-missing_chapter_01'
        repo_name = 'aab_obs_text_obs'
        expected_warnings = 0
        expected_errors= 0
        missing_chapters = [1]
        zip_filepath = self.packageFiles(repo_name, file_name)

        # when
        tx = self.doTransformObs(zip_filepath)# verify the output

        #then
        self.verifyTransform(expected_errors, expected_warnings, tx, missing_chapters)


    def test_complete(self):
        """
        Runs the converter and verifies the output
        """

        # given
        file_name = 'aab_obs_text_obs.zip'
        repo_name = 'aab_obs_text_obs'
        expected_warnings = 0
        expected_errors= 0
        zip_filepath = self.preprocessOBS(repo_name, file_name)

        # when
        tx = self.doTransformObs(zip_filepath)# verify the output

        #then
        self.verifyTransform(expected_errors, expected_warnings, tx)


    def test_missing_fragment(self):
        """
        Runs the converter and verifies the output
        """

        # given
        file_name = 'aab_obs_text_obs_missing_fragment_01_01.zip'
        repo_name = 'aab_obs_text_obs'
        expected_warnings = 1
        expected_errors= 0
        zip_filepath = self.preprocessOBS(repo_name, file_name)

        # when
        tx = self.doTransformObs(zip_filepath)# verify the output

        #then
        self.verifyTransform(expected_errors, expected_warnings, tx)


    def test_missing_chapter(self):
        """
        Runs the converter and verifies the output
        """

        # given
        file_name = 'aab_obs_text_obs-missing_chapter_01.zip'
        repo_name = 'aab_obs_text_obs'
        expected_warnings = 0
        expected_errors= 0
        missing_chapters = [1]
        zip_filepath = self.preprocessOBS(repo_name, file_name)

        # when
        tx = self.doTransformObs(zip_filepath)# verify the output

        #then
        self.verifyTransform(expected_errors, expected_warnings, tx, missing_chapters)


    def verifyTransform(self, expected_errors, expected_warnings, tx, missing_chapters = []):
        # 07 JAN 2017, NB: currently just one html file is being output, all.html
        files_to_verify = []
        files_missing = []
        for i in range(1, 51):
            file_name = str(i).zfill(2) + '.html'
            if not i in missing_chapters:
                files_to_verify.append(file_name)
            else:
                files_missing.append(file_name)

        for file_to_verify in files_to_verify:
            file_name = os.path.join(self.out_dir, file_to_verify)
            self.assertTrue(os.path.isfile(file_name), 'OBS HTML file not found: {0}'.format(file_name))

        for file_to_verify in files_missing:
            file_name = os.path.join(self.out_dir, file_to_verify)
            self.assertFalse(os.path.isfile(file_name), 'OBS HTML file present, but should not be: {0}'.format(file_name))

        file_name = os.path.join(self.out_dir, 'all.html')
        self.assertTrue(os.path.isfile(file_name), 'OBS HTML file not found: {0}'.format(file_name))
        for warning in tx.warnings:
            print("Warning: " + warning)
        for error in tx.errors:
            print("Error: " + error)
        self.assertEqual(len(tx.warnings), expected_warnings)
        self.assertEqual(len(tx.errors), expected_errors)


    def doTransformObs(self, zip_filepath):
        self.out_dir = tempfile.mkdtemp(prefix='txOBS_Test_')
        with closing(TransformOBS(None, self.out_dir, True)) as tx:
            tx.run(zip_filepath)
        return tx

    def preprocessOBS(self, repo_name, file_name): # emulates the preprocessing of the raw files
        file_path = os.path.join(self.resources_dir, file_name)

        # 1) unzip the repo files
        self.temp_dir = tempfile.mkdtemp(prefix='repo_')
        unzip(file_path, self.temp_dir)
        repo_dir = os.path.join(self.temp_dir, repo_name)
        if not os.path.isdir(repo_dir):
            repo_dir = file_path

        # 2) Get the manifest file or make one if it doesn't exist based on meta.json, repo_name and file extensions
        manifest_path = os.path.join(repo_dir, 'manifest.json')
        if not os.path.isfile(manifest_path):
            manifest_path = os.path.join(repo_dir, 'project.json')
            if not os.path.isfile(manifest_path):
                manifest_path = None
        meta_path = os.path.join(repo_dir, 'meta.json')
        meta = None
        if os.path.isfile(meta_path):
            meta = MetaData(meta_path)
        manifest = Manifest(file_name=manifest_path, repo_name=repo_name, files_path=repo_dir, meta=meta)

        # run OBS Preprocessor
        self.temp_dir2 = tempfile.mkdtemp(prefix='output_')
        compiler = TsObsMarkdownPreprocessor(manifest, repo_dir, self.temp_dir2)
        compiler.run()

        # 3) Zip up the massaged files
        # context.aws_request_id is a unique ID for this lambda call, so using it to not conflict with other requests
        zip_filename = 'preprocessed.zip'
        zip_filepath = os.path.join(self.temp_dir, zip_filename)
        add_contents_to_zip(zip_filepath, self.temp_dir2)
        if os.path.isfile(manifest_path) and not os.path.isfile(os.path.join(self.temp_dir2, 'manifest.json')):
            add_file_to_zip(zip_filepath, manifest_path, 'manifest.json')

        return zip_filepath

    def packageFiles(self, repo_name, file_name): # emulates the preprocessing of the raw files
        file_path = os.path.join(self.resources_dir, file_name)
        self.temp_dir = tempfile.mkdtemp(prefix='repo_')

        zip_filename = 'preprocessed.zip'
        zip_filepath = os.path.join(self.temp_dir, zip_filename)
        add_contents_to_zip(zip_filepath, file_path)

        return zip_filepath



if __name__ == '__main__':
    unittest.main()
