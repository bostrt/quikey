#!/usr/bin/env python
from pynput.keyboard import Key, Listener, KeyCode, Controller
from threading import Lock
import daemon
import click
import os
import signal
import sys

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
        keyboard = Controller()
        for phrase in phrases:
            self.notifier.add(PhraseHandler(phrase.get('key'), self.db, keyboard))
    
    def notify(self, event=None):
        self.init_phrase_handlers()
        
class ShutdownHook:
    def __init__(self, listener, watch, appDirs):
        self.appDirs = appDirs
        self.watch = watch
        self.listener = listener
        
    def __call__(self, signal, frame):
        self.watch.stop()
        self.listener.stop()
        delete_pid(self.appDirs)

def write_pid(appDirs):
    pidfile = appDirs.cache + 'quikey.pid'
    with open(pidfile, 'w') as f:
        f.write(str(os.getpid()))

def read_pid(appDirs):
    pidfile = appDirs.cache + 'quikey.pid'
    try:
        with open(pidfile, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(pidfile)
        return None

def delete_pid(appDirs):
    pidfile = appDirs.cache + 'quikey.pid'
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
    write_pid(appDirs) # Store the current pid
    listener = Listener(on_press=i)
    with Listener(on_press=i) as listener: # Continue listening until SIGTERM
        signal.signal(signal.SIGTERM, ShutdownHook(listener, watch, appDirs))
        signal.signal(signal.SIGINT, ShutdownHook(listener, watch, appDirs))
        listener.join()

@click.group()
@click.pass_context
def cli(obj):
    pass

@cli.command()
@click.option('--foreground' ,'-f', is_flag=True, required=False, default=False, help='Run the quikey daemon process in foreground.')
@click.option('--buffer-size', '-b', required=False, default=32, help='Size of buffer that stores keystrokes.')
@click.option('--trigger-keys', '-t', multiple=True, required=False, default=['enter', 'space'], help='Trigger keys that indicate the end of a key phrase. The key name should match one from https://pythonhosted.org/pynput/_modules/pynput/keyboard/_base.html#Key')
def start(foreground, buffer_size, trigger_keys):
    appDirs = AppDirectories() # XDG folders
    pid = read_pid(appDirs)
    daemon_log = appDirs.data+'/qkdaemon.log'

    if pid:
        try:
            os.kill(int(pid), 0)
            print('Quikey daemon is already running (pid: %s).' % pid)
            return
        except OSError:
            pass
    if foreground:
        main(foreground, buffer_size, trigger_keys)
    else:
        daemon_log_f = open(daemon_log, 'w+')
        with daemon.DaemonContext(stdout=daemon_log_f,stderr=daemon_log_f):
            main(foreground, buffer_size, trigger_keys)

@cli.command()
def stop():
    # Send SIGTERM signal
    appDirs = AppDirectories() # XDG folders
    pid = read_pid(appDirs)
    if pid is None:
        print("No Quikey daemon currently running.")
        return
    try:
        os.kill(int(pid), signal.SIGTERM)
    except ProcessLookupError:
        print("No Quikey daemon currently running (tried killing non-existent pid %s)." % pid)
        delete_pid(appDirs)

@cli.command()
def status():
    # Check process existence
    appDirs = AppDirectories() # XDG folders
    pid = read_pid(appDirs)
    if pid is None:
        print ("No Quikey daemon is currently running")
        sys.exit(1)
    try:
        os.kill(int(pid), 0)
    except OSError:
        print ("No Quikey daemon is currently running")
        sys.exit(1)
    else:
        print ("Quikey daemon running (PID: " + pid +")")
        return