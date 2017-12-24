from peewee import *

db = SqliteDatabase('./test.db')

class Phrase(Model):
    key = CharField(index=True,unique=True)
    value = CharField()
    class Meta:
        database = db

class PhraseStore:
    def get(key):
        try:
            p = Phrase.get(Phrase.key == key)
            return p.value
        except Phrase.DoesNotExist:
            return None
        
    def put(key, value):
        p = Phrase(key=key, value=value)
        p.save()
        
    def update(key, value):
        try:
            p = Phrase.get(Phrase.key == key)
            p.value = value
            p.save()
            return True
        except Phrase.DoesNotExist:
            return False
        
    def delete(key):
        try:
            p = Phrase.get(Phrase.key == key)
            if p is not None:
                p.delete_instance()
                return True
            else:
                # No phrase found with key
                return False
        except Phrase.DoesNotExist:
            # Someting bad happened during deletion.
            return False
        
    def get_all():
        return Phrase.select()
