#!/usr/bin/env python
from pynput.keyboard import Key, Controller, Listener, KeyCode
from threading import Lock
from xdg import XDG_DATA_HOME, XDG_CONFIG_HOME, XDG_CACHE_HOME
import click
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
    # Initialize all components and hook them up.
    appDirs = AppDirectories() # XDG folders
    config = get_config(appDirs) # Read config
    notifier = Notifier(typelock) # Create the notifier that calls to each phrase handler
    database = Database(appDirs, config) # Read database in
    dbchange = DatabaseChangeHandler(notifier, database)
    watch = InotifyWatch(database.dbFile) 
    watch.add_observer(dbchange)  # Watch for changes in database outside this process
    i = InputHandler(typelock, notifier, config['main']) # Accepts keyboard inputs
    watch.start()
    i.add_handler(DeleteHandler()) # Special behavior for deletes
    i.add_handler(AlphaNumHandler()) # Standard behavior for everything else
    write_pid() # Store the current pid
    with Listener(on_press=i) as listener: # Continue listening until SIGTERM
        signal.signal(signal.SIGTERM, ShutdownHook(listener, watch))
        listener.join()

@click.group()
@click.pass_context
def cli(obj):
    pass

@cli.command()
@click.option('--foreground' ,'-f', required=False, default=False, help='Run the quikey daemon process in foreground.')
@click.option('--buffer-size', '-b', required=False, default=32, help='Size of buffer that stores keystrokes.')
@click.option('--trigger-keys', '-t', multiple=True, required=False, default='enter', help='Trigger keys that indicate the end of a key phrase. The key name should match one from https://pythonhosted.org/pynput/_modules/pynput/keyboard/_base.html#Key')
@click.pass_context
def start(ctx, foreground, buffer_size, trigger_keys):
    main()

if __name__=='__main__':
    cli(obj={})
