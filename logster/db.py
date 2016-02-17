from collections import OrderedDict

from tornado.ioloop import IOLoop
from tornado.concurrent import Future

import pymongo

from motor.motor_tornado import MotorClient
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from .conf import config
from .exceptions import DbError


_db = None


def connect_to_db(async=True, use_asyncio=False):
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

    if async and use_asyncio:
        client_cls = AsyncIOMotorClient
    elif async and not use_asyncio:
        client_cls = MotorClient
    else:
        client_cls = MongoClient

    conn_str = 'mongodb://' + auth + dest + auth_db
    db_client = client_cls(conn_str)

    db = getattr(db_client, db_conf['dbName'])

    return db_client, db


class ModelField:
    def __init__(self):
        pass


class StringField(ModelField):
    def __init__(self):
        pass


class IntegerField(ModelField):
    def __init__(self):
        pass


class ModelMeta(type):
    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        return OrderedDict()

    def __new__(cls, name, bases, attrs):
        if 'collection_name' not in attrs:
            attrs['collection_name'] = name.lower()

        fields = OrderedDict()
        for attr, attr_val in attrs.items():
            if not isinstance(attr_val, ModelField):
                continue

            fields[attr] = attr_val

        for field in fields.keys():
            attrs.pop(field)

        attrs['_declared_fields'] = fields

        return super().__new__(cls, name, bases, dict(attrs))


class Model(metaclass=ModelMeta):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if k in self._declared_fields:
                setattr(self, k, v)

    @classmethod
    def find(cls, **kwargs):
        return Collection(cls).find(**kwargs)

    @classmethod
    def find_one(cls, **kwargs):
        return Collection(cls).find_one(**kwargs)


def get_db(conn_str=None, db_name=None):
    global _db

    if _db is None:
        _db = MongoClient(conn_str)[db_name]

    return _db


class Collection:
    def __init__(self, model_cls, db=None):
        if not issubclass(model_cls, Model):
            raise ValueError(
                'Class "%s" is not a subclass of "logster.db.Model" class',
                model_cls.__name__)

        self.model_cls = model_cls
        self.collection = (db or get_db())[model_cls.collection_name]
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

    def find_one_async(self, **kwargs):
        col_fut = self.collection.find_one(kwargs)
        fut = Future()

        def cb(result, error):
            r = self.model_cls(**result) if result is not None else None
            fut.set_result(r)

        IOLoop.add_future(col_fut, cb)

        return fut

    def find_one(self, **kwargs):
        data = self.collection.find_one(kwargs)
        if data is not None:
            return self.model_cls(**data)
        return None

    def __iter__(self):
        if not self.cursor:
            raise DbError('You must invoke `.find()` before iterating')

        if not self.result:
            self.result = list(self.cursor)

        return iter(self.result)
