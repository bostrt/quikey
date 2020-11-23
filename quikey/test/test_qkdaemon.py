import unittest
from unittest import mock
import tempfile
from shutil import rmtree
from os import path, getpid

from quikey.directories import AppDirectories
from quikey.qkdaemon import write_pid, read_pid, delete_pid, ShutdownHook, DatabaseChangeHandler

class PidManagementTestCase(unittest.TestCase):
    def setUp(self):
        self.data = tempfile.mkdtemp()
        self.config = tempfile.mkdtemp()
        self.cache = tempfile.mkdtemp()
        self.appDirs = AppDirectories(self.data, self.config, self.cache)
    
    def tearDown(self):
        rmtree(self.data)
        rmtree(self.config)
        rmtree(self.cache)

    def testWritePid(self):
        write_pid(self.appDirs)
        self.assertTrue(path.exists(path.join(self.appDirs.cache, 'quikey.pid')))

    def testReadPid(self):
        write_pid(self.appDirs)
        p = read_pid(self.appDirs)
        self.assertIsNotNone(p)
        
        self.assertEqual(getpid(), int(p))

    def testDeletePid(self):
        write_pid(self.appDirs)
        delete_pid(self.appDirs)
        self.assertFalse(path.exists(path.join(self.appDirs.cache, 'quikey.pid')))    

class ShutdownHookTestCase(unittest.TestCase):
    def setUp(self):
        self.data = tempfile.mkdtemp()
        self.config = tempfile.mkdtemp()
        self.cache = tempfile.mkdtemp()
        self.appDirs = AppDirectories(self.data, self.config, self.cache)
        write_pid(self.appDirs)

    def tearDown(self):
        pass

    @mock.patch('pynput.keyboard.Listener')
    @mock.patch('quikey.filewatch.InotifyWatch')
    def testHookCalled(self, listener, inotify):
        hook = ShutdownHook(listener, inotify, self.appDirs)
        hook(0, None)
        listener.stop.assert_called_with()
        inotify.stop.assert_called_with()        

if __name__ == '__main__':
    unittest.main()