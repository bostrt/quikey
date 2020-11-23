import unittest
from unittest import mock
import tempfile
from collections import deque

from pynput.keyboard import KeyCode, Key

from quikey.input import PhraseHandler, Notifier, AlphaNumHandler, DeleteHandler, SpaceHandler

class PhraseHandlerTestCase(unittest.TestCase):
    @mock.patch('pynput.keyboard.Controller')
    @mock.patch('quikey.models.Database')
    def setUp(self, controller, db):
        self.controller = controller
        self.db = db
        self.phraseHandler = PhraseHandler('test', self.db, self.controller)

    def testNotifyMatch(self):
        self.assertTrue(self.phraseHandler.notify('test'))
        self.phraseHandler.keyboard.type.assert_called()

    def testNotifyNoMatch(self):
        self.assertFalse(self.phraseHandler.notify('asdf'))

    def tearDown(self):
        pass

class NotifierTestCase(unittest.TestCase):
    @mock.patch('threading.Lock')
    def setUp(self, lock):
        self.notifier = Notifier(lock)

    @mock.patch('quikey.qkdaemon.DatabaseChangeHandler')
    def testAddObserver(self, observer):
        self.notifier.add(observer)
        self.assertEqual(1, len(self.notifier.observers))

    @mock.patch('quikey.qkdaemon.DatabaseChangeHandler')
    def testClearObservers(self, observer):
        self.notifier.add(observer)
        self.notifier.clear()
        self.assertEqual(0, len(self.notifier.observers))

    @mock.patch('quikey.qkdaemon.DatabaseChangeHandler')
    def testNotifyMatch(self, observer):
        observer.notify = mock.MagicMock(return_value=True)
        self.notifier.add(observer)
        self.notifier.notify('x')
        self.notifier.lock.acquire.assert_called()  
        self.notifier.lock.release.assert_called()
        self.notifier.observers[0].notify.assert_called()

    @mock.patch('quikey.qkdaemon.DatabaseChangeHandler')
    def testNotifyNoMatch(self, observer):
        observer.notify = mock.MagicMock(return_value=False)
        self.notifier.add(observer)
        self.notifier.notify('x')
        self.notifier.lock.acquire.assert_called()  
        self.notifier.lock.release.assert_called()
        self.notifier.observers[0].notify.assert_called()

class AlphaNumHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.handler = AlphaNumHandler()
    
    def testVerifyMatch(self):
        self.assertTrue(self.handler.verify(KeyCode.from_char('x')))
        self.assertTrue(self.handler.verify(KeyCode.from_char('Z')))
        self.assertTrue(self.handler.verify(KeyCode.from_char('0')))
        self.assertFalse(self.handler.verify(Key.ctrl))

    def testOnKey(self):
        buff = deque(maxlen=1)
        ret = self.handler.onkey(KeyCode.from_char('z'), buff)
        self.assertTrue(ret)
        self.assertEqual(1, len(buff))

    def testOnKeyFullBuff(self):
        buff = deque(maxlen=4)
        self.handler.onkey(KeyCode.from_char('a'), buff)
        self.handler.onkey(KeyCode.from_char('b'), buff)
        self.handler.onkey(KeyCode.from_char('c'), buff)
        self.handler.onkey(KeyCode.from_char('d'), buff)
        self.handler.onkey(KeyCode.from_char('e'), buff)
        self.assertEqual(4, len(buff))
        self.assertEqual('b', buff.popleft())
        self.assertEqual('c', buff.popleft())
        self.assertEqual('d', buff.popleft())
        self.assertEqual('e', buff.popleft())

    def testOnKeyBadKeys(self):
        buff = deque(maxlen=4)
        self.handler.onkey(KeyCode.from_char('a'), buff)
        self.handler.onkey(Key.alt, buff)
        self.handler.onkey(KeyCode.from_char('b'), buff)
        self.handler.onkey(KeyCode.from_char('c'), buff)
        self.handler.onkey(KeyCode.from_char('d'), buff)
        self.assertEqual(4, len(buff))

class DeleteHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.handler = DeleteHandler()
    
    def testVerify(self):
        self.assertTrue(self.handler.verify(Key.backspace))
        self.assertFalse(self.handler.verify(Key.ctrl))
    
    def testOnKey(self):
        buff = deque(maxlen=4)
        buff.append('a')
        buff.append('b')
        buff.append('c')
        ret = self.handler.onkey(Key.backspace, buff)
        self.assertTrue(ret)
        self.assertEqual(2, len(buff))
        self.assertEqual('b', buff.pop())
        self.assertEqual('a', buff.pop())

class SpaceHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.handler = SpaceHandler()
    
    def testOnKey(self):
        buff = deque(maxlen=2)
        self.assertFalse(self.handler.onkey(Key.alt, buff))
        self.assertTrue(self.handler.onkey(Key.space, buff))
        self.assertEqual(1, len(buff))
        self.handler.onkey(Key.space, buff)
        self.handler.onkey(Key.space, buff)
        self.assertEqual(2, len(buff))

if __name__ == '__main__':
    unittest.main()