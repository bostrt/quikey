#!/usr/bin/env python
from pynput.keyboard import Key, Listener, KeyCode
from threading import Lock
import daemon
from xdg import XDG_DATA_HOME, XDG_CONFIG_HOME, XDG_CACHE_HOME
import click
import os
import signal

from quikey.models import Database
from quikey.directories import AppDirectories
from quikey.filewatch import InotifyWatch
from quikey.input import PhraseHandler, Notifier, InputHandler, AlphaNumHandler, DeleteHandler, SpaceHandler

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
            self.notifier.add(PhraseHandler(phrase.get('key'), self.db))
    
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
    with open(pidfile, 'w') as f:
        f.write(str(os.getpid()))

def read_pid():
    pidfile = XDG_CACHE_HOME + '/quikey/quikey.pid'
    try:
        with open(pidfile, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None

def delete_pid():
    pidfile = XDG_CACHE_HOME + '/quikey/quikey.pid'
    os.remove(pidfile)

def main(foreground, buffer_size, trigger_keys):
    # Initialize all components and hook them up.
    appDirs = AppDirectories() # XDG folders
    notifier = Notifier(typelock) # Create the notifier that calls to each phrase handler
    database = Database(appDirs) # Read database in
    dbchange = DatabaseChangeHandler(notifier, database)
    watch = InotifyWatch(database.dbFile) 
    watch.add_observer(dbchange)  # Watch for changes in database outside this process
    i = InputHandler(typelock, notifier, buffer_size, trigger_keys) # Accepts keyboard inputs
    watch.start()
    i.add_handler(DeleteHandler()) # Special behavior for deletes
    i.add_handler(AlphaNumHandler()) # Standard behavior for everything else
    i.add_handler(SpaceHandler())
    write_pid() # Store the current pid
    listener = Listener(on_press=i)
    with Listener(on_press=i) as listener: # Continue listening until SIGTERM
        signal.signal(signal.SIGTERM, ShutdownHook(listener, watch))
        signal.signal(signal.SIGINT, ShutdownHook(listener, watch))
        listener.join()

@click.group()
@click.pass_context
def cli(obj):
    pass

@cli.command()
@click.option('--foreground' ,'-f', is_flag=True, required=False, default=False, help='Run the quikey daemon process in foreground.')
@click.option('--buffer-size', '-b', required=False, default=32, help='Size of buffer that stores keystrokes.')
@click.option('--trigger-keys', '-t', multiple=True, required=False, default=['enter', 'space'], help='Trigger keys that indicate the end of a key phrase. The key name should match one from https://pythonhosted.org/pynput/_modules/pynput/keyboard/_base.html#Key')
@click.option('--daemon-log', required=False, default=os.path.realpath(XDG_DATA_HOME+'/quikey/qkdaemon.log'), type=click.File('w'), help='Output log file when running in daemonized mode.')
def start(foreground, buffer_size, trigger_keys, daemon_log):
    pid = read_pid()
    if pid:
        print('Quikey daemon is already running (pid: %s).' % pid)
        exit
    if foreground:
        main(foreground, buffer_size, trigger_keys)
    else:
        with daemon.DaemonContext(stdout=daemon_log,stderr=daemon_log):
            main(foreground, buffer_size, trigger_keys)

@cli.command()
def stop():
    # Send SIGTERM signal
    pid = read_pid()
    if pid is None:
        print("No Quikey daemon currently running.")
        return
    try:
        os.kill(int(pid), signal.SIGTERM)
    except ProcessLookupError:
        print("No Quikey daemon currently running (tried killing non-existent pid %s)." % pid)
        delete_pid()
