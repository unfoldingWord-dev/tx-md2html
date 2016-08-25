from __future__ import print_function, unicode_literals
import os
import shutil
import tempfile
from contextlib import closing
import unittest
from functions.convert.transform_obs import TransformOBS


class TestTransformOBS(unittest.TestCase):

    def setUp(self):
        """
        Runs before each test
        """
        self.out_dir = ''

    def tearDown(self):
        """
        Runs after each test
        """
        # delete temp files
        if os.path.isdir(self.out_dir):
            shutil.rmtree(self.out_dir, ignore_errors=True)

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
        This tests that the temp directory is deleted when the class is closed
        """

        with closing(TransformOBS('', '', True)) as tx:
            temp_dir = tx.temp_dir

            # verify the directory is present
            self.assertTrue(os.path.isdir(temp_dir))

        # now it should have been deleted
        self.assertFalse(os.path.isdir(temp_dir))

    def test_run(self):
        """
        Runs the converter and verifies the output
        """
        # test with the English OBS
        repo = 'https://git.door43.org/Door43/en-obs.git'
        self.out_dir = tempfile.mkdtemp(prefix='txOBS_Test_')
        with closing(TransformOBS(repo, self.out_dir, True)) as tx:
            tx.run()

        # verify the output
        files_to_verify = []
        for i in range(1, 51):
            files_to_verify.append(str(i).zfill(2) + '.html')

        for file_to_verify in files_to_verify:

            file_name = os.path.join(self.out_dir, file_to_verify)
            self.assertTrue(os.path.isfile(file_name), 'OBS HTML file not found: {0}'.format(file_name))


if __name__ == '__main__':
    unittest.main()
