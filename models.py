from peewee import *

db = SqliteDatabase('./test.db')

class Phrase(Model):
    key = CharField(index=True,unique=True)
    value = CharField()
    class Meta:
        database = db

class PhraseStore:
    def get(key):
        p = Phrase.get(Phrase.key == key)
        return p.value
    def put(key, value):
        p = Phrase(key=key, value=value)
        p.save()
    def get_all():
        return Phrase.select()
