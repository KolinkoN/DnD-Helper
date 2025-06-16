import sqlite3
from abc import ABC, abstractmethod


conn = sqlite3.connect('bot.db')
cursor = conn.cursor()

class NoMethodsMeta(type):
    def __new__(mcs, name, bases, namespace):
        for key, value in namespace.items():
            if callable(value) and not key.startwith("__"):
                raise TypeError(f"Methods in class '{name}' is not allowed, found '{key}'")

class DBSubClass:
    table: str

    @abstractmethod
    @classmethod
    def get(cls):
        pass

    @abstractmethod
    @classmethod
    def update(cls):
        pass

    @abstractmethod
    @classmethod
    def delete(cls):
        pass

class DB(metaclass=NoMethodsMeta):


    class UserSpells(DBSubClass):
        table = "user_spells"

        @classmethod
        def get(cls):
            pass

        @classmethod
        def update(cls):
            pass
        
        @classmethod
        def delete(cls):
            pass

    class AllSpells(DBSubClass):
        table = "all_spells"

        @classmethod
        def get(cls):
            return super().get()
        
        @classmethod
        def update(cls):
            return super().update()
        
        @classmethod
        def delete(cls):
            return super().delete()
        

    class Characters(DBSubClass):
        table = "characters"

        @classmethod
        def get(cls):
            return super().get()
        
        @classmethod
        def update(cls):
            return super().update()
        
        @classmethod
        def delete(cls):
            return super().delete()
        

    class Scenes(DBSubClass):
        table = "scenes"

        @classmethod
        def get(cls):
            return super().get()
        
        @classmethod
        def update(cls):
            return super().update()
        
        @classmethod
        def delete(cls):
            return super().delete()
        
    class Campaign(DBSubClass):
        table = "campaign"

        @classmethod
        def get(cls):
            return super().get()
        
        @classmethod
        def update(cls):
            return super().update()
        
        @classmethod
        def delete(cls):
            return super().delete()


        
