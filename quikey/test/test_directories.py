import unittest
import tempfile
from shutil import rmtree
from os import path

from quikey.directories import AppDirectories

class AppDirectoriesTestCase(unittest.TestCase):
    def setUp(self):
        self.data = tempfile.mkdtemp()
        self.config = tempfile.mkdtemp()
        self.cache = tempfile.mkdtemp()
        self.appDirs = AppDirectories(self.data, self.config, self.cache)
    
    def tearDown(self):
        rmtree(self.data)
        rmtree(self.config)
        rmtree(self.cache)

    def testAppDirectories(self):
        self.assertEqual(path.join(self.data, 'quikey/'), self.appDirs.data)
        self.assertEqual(path.join(self.config, 'quikey/'), self.appDirs.config)
        self.assertEqual(path.join(self.cache, 'quikey/'), self.appDirs.cache)

if __name__ == '__main__':
    unittest.main()