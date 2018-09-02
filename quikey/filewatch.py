from threading import Thread
from inotify_simple import INotify, flags

class InotifyWatch(Thread):
    """
    Watches for inotify notifications when the databsae file changes. This
    sends notification to any observers added to this monitor.
    """
    def __init__(self, dbfile):
        super().__init__()
        self.inotify = INotify()
        self.watch = self.inotify.add_watch(dbfile, flags.MODIFY)
        self.running = True
        self.observers = []
        
    def stop(self):
        self.inotify.rm_watch(self.watch)
        self.running = False
    
    def run(self):
        while self.running:
            for event in self.inotify.read():
                for observer in self.observers:
                    observer.notify()
    
    def add_observer(self, observer):
        self.observers.append(observer)
