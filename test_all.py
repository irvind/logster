import pytest
import random

import pymongo

from logster.db import Model, get_db
from logster import conf


class TempCollection:
    def __init__(self, db, name, initial_data=None):
        self.db = db
        self.name = name
        self.initial_data = initial_data

    def __enter__(self):
        self.col = self.db[self.name]
        if self.initial_data is not None:
            self.col.insert(self.initial_data)

        return self.col

    def __exit__(self, type, value, traceback):
        self.col.drop()


class DbTests:
    def __init__(self):
        self.db = get_db(conf.DB_CONN_STRING, conf.TEST_DB_NAME)

    def test_collection(self, initial_data=None):
        name = 'test%d' % random.randint(10000, 99999)
        if initial_data is not None:
            pass

        return TempCollection(self.db, name, initial_data)


@pytest.fixture(scope='module')
def db():
    return DbTests()


def test_db_fixture(db):
    data = [{'test': 42}, {'test': 43}]

    with db.test_collection(initial_data=data) as col:
        assert isinstance(col, pymongo.collection.Collection)
        doc = col.find_one({'test': 42})

        assert doc is not None
        assert doc['test'] == 42


def test_find_in_collection(db):
    data = [
        {'name': 'Ginger', 'age': 2},
        {'name': 'Kleo', 'age': 4},
        {'name': 'Fluffy', 'age': 7}
    ]

    with db.test_collection(initial_data=data) as col:
        class Kitteh(Model):
            collection_name = col.name
            db = col.database

        cat = Kitteh.find_one(name='Ginger')
        assert cat.name == 'Ginger'
