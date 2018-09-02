#!/usr/bin/env python
from pynput.keyboard import Key, Controller, Listener, KeyCode
from threading import Lock
from xdg import XDG_DATA_HOME, XDG_CONFIG_HOME, XDG_CACHE_HOME
import os
import signal
import configparser
from configparser import NoSectionError

from models import Database
from directories import AppDirectories
from filewatch import InotifyWatch
from input import PhraseHandler, Notifier, InputHandler, AlphaNumHandler, DeleteHandler

typelock = Lock()

class DatabaseChangeHandler:
    def __init__(self, notifier, database):
        self.notifier = notifier
        self.db = database
        self.init_phrase_handlers()

    def init_phrase_handlers(self):
        self.notifier.clear()
        #phrases = PhraseStore.get_all()
        phrases = self.db.all()
        for phrase in phrases:
            self.notifier.add(PhraseHandler(phrase['key'], self.db))
    
    def notify(self, event=None):
        self.init_phrase_handlers()
        
class ShutdownHook:
    def __init__(self, listener, watch):
        self.watch = watch
        self.listener = listener
        
    def __call__(self, signal, frame):
        self.watch.stop()
        self.listener.stop()
        delete_pid()

def write_pid():
    pidfile = XDG_CACHE_HOME + '/quikey/quikey.pid'
    open(pidfile, 'w').write(str(os.getpid()))

def delete_pid():
    pidfile = XDG_CACHE_HOME + '/quikey/quikey.pid'
    os.remove(pidfile)

def get_config(directories, iniFile='quikey.ini'):
    config = configparser.ConfigParser()
    config.read(directories.config + iniFile)
    if not config.has_section('main'):
        err = 'Configuration file "%s" missing required [main] section.' % (directories.config + iniFile)
        raise NoSectionError(err)
    return config

def main():
    appDirs = AppDirectories()
    config = get_config(appDirs)
    notifier = Notifier(typelock)
    database = Database(appDirs, config)
    dbchange = DatabaseChangeHandler(notifier, database)
    watch = InotifyWatch(database.dbFile)
    watch.add_observer(dbchange)
    i = InputHandler(typelock, notifier, config['main'])
    watch.start()
    i.add_handler(DeleteHandler())        
    i.add_handler(AlphaNumHandler())
    write_pid()
    with Listener(on_press=i) as listener:
        signal.signal(signal.SIGTERM, ShutdownHook(listener, watch))
        listener.join()

if __name__=='__main__':
    main()
