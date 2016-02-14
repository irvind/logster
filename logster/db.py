import pymongo

from motor.motor_tornado import MotorClient
from pymongo import MongoClient

from .conf import config
from .exceptions import DbError


def connect_to_db(async=True):
    db_conf = config['db']

    with_auth = db_conf.get('user') and db_conf.get('password')
    if with_auth:
        auth = '{user}:{password}@'.format(**db_conf)
        if db_conf.get('authDbName'):
            auth_db = '/' + db_conf['authDbName']
    else:
        auth = ''
        auth_db = ''

    dest = '{host}:{port}'.format(**db_conf)

    conn_str = 'mongodb://' + auth + dest + auth_db
    client_cls = MotorClient if async else MongoClient
    db_client = client_cls(conn_str)

    db = getattr(db_client, db_conf['dbName'])

    return db_client, db


class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        if 'collection_name' not in attrs:
            attrs['collection_name'] = name.lower()

        return super().__new__(cls, name, bases, attrs)


class Model(metaclass=ModelMeta):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def find(cls, **kwargs):
        return Collection(cls).find(**kwargs)

    @classmethod
    def find_one(cls, **kwargs):
        return Collection(cls).find_one(**kwargs)


# db = connect_to_db(False)[1]


class Collection:
    def __init__(self, model_cls, db):
        if not issubclass(model_cls, Model):
            raise ValueError(
                'Class "%s" is not a subclass of "logster.db.Model" class',
                model_cls.__name__)

        self.model_cls = model_cls
        self.collection = db[model_cls.collection_name]
        self.result = None
        self.cursor = None

    def find(self, **kwargs):
        self.result = None
        self.cursor = self.collection.find(kwargs)
        return self

    def sort(self, *args):
        if self.cursor is None:
            raise DbError('You must invoke `.find()` before sorting')

        sorters = [
            (arg, pymongo.ASCENDING) if arg[0] == '-'
            else (arg[1:], pymongo.DESCENDING) for arg in args]

        self.cursor = self.cursor.sort(sorters)
        return self

    def find_one(self, **kwargs):
        data = self.collection.find_one(kwargs)
        if data is not None:
            return self.model_cls(**data)
        return None

    def __iter__(self):
        if not self.result and not self.cursor:
            raise DbError()

        if not self.result:
            self.result = list(self.cursor)

        return iter(self.result)
