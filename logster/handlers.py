import random
import json
import logging

import pymongo

from bson.objectid import ObjectId

from tornado import gen
from tornado.web import RequestHandler, authenticated
from tornado.websocket import WebSocketHandler

logger = logging.getLogger('webapp')


class BaseHandler(RequestHandler):
    @property
    def db(self):
        return self.application.db

    @property
    def json_body(self):
        if self.request.body:
            return None

        body = self.request.body.decode('utf-8')

        return json.loads(body) if body else None

    def get_current_user(self):
        return self.get_secure_cookie('user')


class IndexHandler(BaseHandler):
    test_log = 'test_log'

    @gen.coroutine
    @authenticated
    def get(self):
        log_entries = yield self.db.entries.find({
            'log': self.test_log
        }).sort('order', pymongo.DESCENDING).limit(5).to_list(None)

        context = {
            'log_entries': [e['content'] for e in reversed(log_entries)],
            'token': random.randint(0, 999)
        }

        self.render('index.html', **context)


class LoginHandler(BaseHandler):
    def get(self):
        self._render_template()

    @gen.coroutine
    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')

        success, error = yield self._authenticate_user(username, password)

        if success:
            self.set_secure_cookie('user', username)
            self.redirect('/')
        else:
            self._render_template(error)

    @gen.coroutine
    def _authenticate_user(self, username, password):
        user = yield self.db.users.find_one({'username': username})
        if user is None:
            return False, 'Login does not exist'

        if user.get('password') != password:
            return False, 'Password is invalid'

        return True, None

    def _render_template(self, error=''):
        self.render('login.html', error=error)


class LogoutHandler(BaseHandler):
    @authenticated
    def get(self):
        self.clear_cookie('user')
        self.redirect('/')


_trigger_counter = 0


class TestTriggerHandler(BaseHandler):
    def get(self):
        global _trigger_counter

        for _, v in _test_socket_pool.items():
            v.send_message('Message #{}'.format(_trigger_counter))

        _trigger_counter += 1

        logger.debug('Triggered (counter=%s)', _trigger_counter - 1)


_test_socket_pool = {}


class TestSocketHandler(WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        self.token = self.get_argument('token')

        _test_socket_pool[self.token] = self

        logger.debug('Socket handler was added to the pool (token=%s)',
                     self.token)

    def on_message(self, message):
        pass

    def on_close(self):
        del _test_socket_pool[self.token]

        logger.debug('Socket handler was removed from the pool (token={})',
                     self.token)

    def send_message(self, msg):
        self.write_message(json.dumps({'message': msg}))

        logger.debug('Message was sent (token=%s, msg="%s")',
                     self.token, msg)


class NotificationsHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        if self.request.remote_ip != '127.0.0.1':
            return

        body = self.json_body

        logger.info('Scanner notification received. Body: %s', body)

        log = yield self.db.logs.find_one({
            '_id': ObjectId(body['log_id'])
        })

        entries = yield self.db.entries.find({
            '_id': {
                '$in': [ObjectId(ent) for ent in body['entry_ids']]
            }
        }).sort('order').to_list(None)

        if log['name'] != 'test_log':
            # todo: until now only accept 'test_log' entry notifications
            return

        for _, v in _test_socket_pool.items():
            for ent in entries:
                v.send_message(ent['content'])
