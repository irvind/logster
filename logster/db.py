from motor.motor_tornado import MotorClient
from pymongo import MongoClient

from .conf import config


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