from tinydb import TinyDB, Query
from datetime import datetime

class Database():
    def __init__(self, appDirs, dbFile='phrases.json'):
        self.appDirs = appDirs
        self.dbFile = self.appDirs.data + '/' + dbFile
        # Ensure database file exists
        self.db = TinyDB(self.dbFile)

    def get(self, key):
        phrase = Query()
        phraseDict = self.db.get(phrase.key == key)
        if phraseDict is None:
            return None
        return phraseDict.get('value')

    def put(self, key, value, tags=None):
        now = datetime.utcnow().isoformat()
        phrase = {'key': key, 'value': value, 'tags': tags, 'updated': now}
        self.db.insert(phrase)

    def update(self, key, value, tags=None):
        now = datetime.utcnow().isoformat()
        phrase = Query()
        self.db.update({'key': key, 'value': value, 'updated': now}, phrase.key == key)

    def delete(self, key):
        phrase = Query()
        return self.db.remove(phrase.key == key)

    def all(self):
        return self.db.all()
