from peewee import *
from playhouse.fields import ManyToManyField
from xdg import XDG_DATA_HOME

db = SqliteDatabase(XDG_DATA_HOME + '/quikey/phrases.db')

class Tag(Model):
    name = CharField(index=True,unique=True)
    class Meta:
        database = db

class Phrase(Model):
    key = CharField(index=True,unique=True)
    value = CharField()
    tags = ManyToManyField(Tag, related_name='phrases')
    class Meta:
        database = db

def initialize_db():
    db.create_tables([Tag, Phrase, Phrase.tags.get_through_model()], safe=True)

class PhraseStore:
    """
    A simple abstraction on database access.
    """
    def get(key):
        try:
            p = Phrase.get(Phrase.key == key)
            return p.value
        except Phrase.DoesNotExist:
            return None
        
    def put(key, value, tags=None):
        p = Phrase(key=key, value=value)
        p.save()        
        if tags is not None:
            for tag in tags:
                t,created = Tag.get_or_create(name=tag)
                p.tags.add(t)
                
    def update(key, value=None, tags=None):
        try:
            p = Phrase.get(Phrase.key == key)
            if value is not None:
                p.value = value
                p.save()
            if tags is not None:
                for tag in tags:
                    t,created = Tag.get_or_create(name=tag)
                    p.tags.add(t)
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
