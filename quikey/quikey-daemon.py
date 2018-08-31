#!/usr/bin/env python
from pynput.keyboard import Key, Controller, Listener, KeyCode
from collections import deque
from threading import Lock
from xdg import XDG_DATA_HOME, XDG_CONFIG_HOME, XDG_CACHE_HOME
import os
import re
import configparser
import signal
from configparser import NoSectionError
from models import Phrase, PhraseStore, initialize_db, db
from monitor import Monitor

typelock = Lock()
keyboard = Controller()

class Observer:
    def notify(self, event):
        pass

class PhraseHandler(Observer):
    """
    Watches for notifications about new incoming phrases. A single 
    PhraseHandler is created for each phrase-key in the database. 
    
    PhraseHandler also "types out" the value matching a phrase-key.
    
    The user input is checked with trailing characters with priority. A regular 
    expression is interanlly created like this: .*<key>. For example, if you 
    have a phrase key called "hello", the regular expression would be: .*hello
    
    If a user types "blahblahhello<Enter>", their phrase would be triggered.
    """
    def __init__(self, key):
        self.key = key
        escaped = re.escape(key)
        self.regex = re.compile('^.*' + escaped + '$')
        
    def notify(self, incomingkey):
        if self.regex.match(incomingkey):
            phrase = PhraseStore.get(self.key)
            self.backspace(len(self.key)+1)
            keyboard.type(phrase)
            return True
        return False
    
    def backspace(self, count):
        i = 0
        while i < count:
            keyboard.press(Key.backspace)
            keyboard.release(Key.backspace)
            i = i + 1

class Notifier(Observer):
    """
    Class composed of PhraseHandlers. Each observer called when new key input
    is ready to be checked against phrase database.
    
    Notifier acquires a global lock while iterating observers. This prevents
    infinite loops when a value being "typed out" contains a phrase-key.
    i.e. we don't want the automated keyboard typing to be picked up by this app.
    """
    def __init__(self, lock):
        self.observers = []
        self.lock = lock
    
    def clear(self):
        self.observers = []
    
    def add(self, observer):
        self.observers.append(observer)
        
    def notify(self, key):
        # Acquire lock to that any output from an observer hanlding the
        # phrase-key do not get piped back into this app.
        self.lock.acquire()        
        for observer in self.observers:
            try:
                if observer.notify(key):
                    # Release lock since one of observers handled the phrase-key.
                    self.lock.release()                    
                    return True
            except:
                # TODO: What types of exceptions would be raised here?
                pass
        # No observers hanlded the phrase-key so go head and release lock.
        self.lock.release()

class AlphaNumHandler:
    """
    Handles alphanumeric input, appending to key input buffer.
    """
    def verify(self, key):
        return type(key) == KeyCode
    
    def onkey(self, key, keybuff):
        if not self.verify(key):
            return False
        
        if len(keybuff) == keybuff.maxlen:
            # Pop off front of queue if at max length.
            keybuff.popleft()
        # Push new input onto end of queue.
        if key.char is not None:
            keybuff.append(key.char)
        return True
        
class DeleteHandler:
    """
    Handles delete/backspace input, adjusting key input buffer.
    """
    def verify(self, key):
        return key == Key.backspace
    
    def onkey(self, key, keybuff):
        if not self.verify(key):
            return False
        if len(keybuff) > 0:
            # Pop off end of queue as long as there is an item in queue.
            keybuff.pop()
        return True

class TriggerPhraseHandler:
    """
    Handles "trigger" keys that tell this app when to look for key 
    substitution phrases.
    """
    def __init__(self, config):
        keyliststr = config.get('triggerkeys', 'enter,space')
        keylistraw = keyliststr.split(',')
        self.triggerkeys = []
        for key in keylistraw:
            key = key.strip()
            if len(key) > 0 and key in Key.__members__:
                self.triggerkeys.append(Key[key])
    
    def verify(self, key):
        return key in self.triggerkeys
    
    def onkey(self, key):
        return self.verify(key)
            
class InputHandler:
    """
    Handles keyboard input, calling each key-specific handler.
    """
    def __init__(self, lock, notifier, config):
        keybuffsize = config.getint('keybuffersize', 32)
        self.keybuff = deque(maxlen=keybuffsize)
        self.lock = lock
        self.notifier = notifier
        self.subhandlers = []
        self.triggerhandler = TriggerPhraseHandler(config)

    def dequetostr(self):
        ret = u''
        for x in self.keybuff:
            ret = ret + x
        return ret        

    def __call__(self, key):
        if self.lock.locked():
            # Skip. Something else has acquired lock.
            return 
        # Check if trigger key pressed
        if self.triggerhandler.onkey(key):
            if self.notifier.notify(self.dequetostr()):
                # A phrase was found and typed out. Clear queue and return.
                self.keybuff.clear()
                return 
        for handler in self.subhandlers:
            result = handler.onkey(key, self.keybuff)
            if result:
                return
            
    def add_handler(self, handler):
        self.subhandlers.append(handler)
    
def backspace(count):
    i = 0
    while i < count:
        keyboard.press(Key.backspace)
        keyboard.release(Key.backspace)
        i = i + 1

class DatabaseChangeHandler(Observer):
    def __init__(self, notifier):
        self.notifier = notifier
        self.init_phrase_handlers()

    def init_phrase_handlers(self):
        self.notifier.clear()
        phrases = PhraseStore.get_all()
        for phrase in phrases:
            self.notifier.add(PhraseHandler(phrase.key))
    
    def notify(self, event=None):
        self.init_phrase_handlers()
        
class ShutdownHook:
    def __init__(self, listener, monitor):
        self.monitor = monitor
        self.listener = listener
        
    def __call__(self, signal, frame):
        self.monitor.stop()
        self.listener.stop()
        delete_pid()
        
def initialize_xdg():
    os.makedirs(XDG_DATA_HOME + '/quikey', exist_ok=True)
    os.makedirs(XDG_CONFIG_HOME + '/quikey', exist_ok=True)    
    os.makedirs(XDG_CACHE_HOME + '/quikey', exist_ok=True)        

def initialize_config():
    config = configparser.ConfigParser()
    config.read(XDG_CONFIG_HOME + '/quikey/quikey.ini')
    if not config.has_section('main'):
        err = 'Configuration file "%s" missing required [main] section.' % (XDG_CONFIG_HOME + '/quikey/quikey.ini')
        raise NoSectionError(err)
    return config

def write_pid():
    pidfile = XDG_CACHE_HOME + '/quikey/quikey.pid'
    open(pidfile, 'w').write(str(os.getpid()))

def delete_pid():
    pidfile = XDG_CACHE_HOME + '/quikey/quikey.pid'
    os.remove(pidfile)
    
def main():
    initialize_xdg();
    config = initialize_config();
    initialize_db()
    notifier = Notifier(typelock)
    dbchange = DatabaseChangeHandler(notifier)
    monitor = Monitor(db.database)
    monitor.add_observer(dbchange)
    i = InputHandler(typelock, notifier, config['main'])
    monitor.start()
    i.add_handler(DeleteHandler())        
    i.add_handler(AlphaNumHandler())
    write_pid()
    with Listener(on_press=i) as listener:
        signal.signal(signal.SIGTERM, ShutdownHook(listener, monitor))
        listener.join()

if __name__=='__main__':
    main()
