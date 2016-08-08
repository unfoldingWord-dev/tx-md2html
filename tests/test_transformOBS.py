from __future__ import print_function, unicode_literals
import os
from contextlib import closing
import unittest
from obs.transform import TransformOBS


class TestTransformOBS(unittest.TestCase):
    def test_close(self):
        """
        This tests that the temp directory is deleted when the class is closed
        """

        with closing(TransformOBS('', '')) as tx:
            temp_dir = tx.temp_dir

            # verify the directory is present
            self.assertTrue(os.path.isdir(temp_dir))
            print('    Temp directory was created: {0}.'.format(temp_dir))

        # now it should have been deleted
        self.assertFalse(os.path.isdir(temp_dir))
        print('    Temp directory was deleted.')

    def test_run(self):
        self.fail()


if __name__ == '__main__':
    unittest.main()
