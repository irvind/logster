import os
import pymongo

from .db import connect_to_db


files_to_check = [
    '/home/irvind/test.log',
    '/home/irvind/test2.log'
]


def run_scanner():
    _, db = connect_to_db(async=False)

    while True:
        try:
            pass
        except KeyboardInterrupt:
            break
