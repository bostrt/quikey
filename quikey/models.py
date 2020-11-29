from os.path import join
from tinydb import TinyDB, Query
from datetime import datetime
from filelock import FileLock


class Database:
    def __init__(self, appDirs, dbFile='phrases.json'):
        self.lock = FileLock(join(appDirs.data, dbFile + '.lock'))
        self.appDirs = appDirs
        self.dbFile = join(self.appDirs.data, dbFile)
        self.db = TinyDB(self.dbFile)

    def get(self, key):
        phrase = Query()
        with self.lock:
            phraseDict = self.db.get(phrase.key == key)
            if phraseDict is None:
                return None
            return phraseDict.get('value')

    def put(self, key, value, tags=None):
        now = datetime.utcnow().isoformat()
        phrase = {'key': key, 'value': value, 'tags': tags, 'updated': now}
        with self.lock:
            self.db.insert(phrase)

    def update(self, key, value, tags=None):
        now = datetime.utcnow().isoformat()
        phrase = Query()
        with self.lock:
            self.db.update({'key': key, 'value': value, 'updated': now}, phrase.key == key)

    def delete(self, key):
        phrase = Query()
        with self.lock:
            return self.db.remove(phrase.key == key)

    def all(self):
        with self.lock:
            return self.db.all()
