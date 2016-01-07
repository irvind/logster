import os
import datetime
import time
import hashlib

from datetime import datetime

import pymongo

from .db import connect_to_db


def file_mtime(path):
    return datetime.fromtimestamp(os.stat(path).st_mtime)


def md5_hex(data):
    # todo
    pass


def run_scanner():
    _, db = connect_to_db(async=False)
    
    try:
        while True:
            _scanner_iter(db)

    except KeyboardInterrupt:
        pass


def _scanner_iter(db):

    def check_log(log):
        mtime, path, log_id = (
            log.get('last_mtime'), 
            log.get('path'), 
            log.get('id'),
        )

        if mtime is not None and mtime >= file_mtime(path):
            # File not changed
            return

        log_entries = list(db.entries.find({'log': log_id}).sort('order'))
        db_lines = [ent['content'] for ent in log_entries]

        with open(path, 'r') as f:
            file_lines = f.readlines()

        if len(file_lines) <= len(db_lines):
            # todo: special case
            return

        old_lines = file_lines[:len(db_lines)]
        new_lines = file_lines[len(db_lines):]

        if md5_hex(old_lines) != md5_hex(db_lines):
            # todo: special case
            return

        last_order = log_entries[len(db_lines)-1]['order']

        new_docs = []
        i = last_order + 1
        for line in new_lines:
            new_docs.append({
                'log': log_id,
                'content': line, 
                'order': i
            })

            i += 1

        db.entries.insert(new_docs)

        _notify_websockets(new_docs)

    for log in db.logs.find():
        check_log(log)

    time.sleep(1)


def _notify_websockets(docs):
    # todo
    pass