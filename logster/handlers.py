import json
import logging

import pymongo

from bson.objectid import ObjectId

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, authenticated
from tornado.websocket import WebSocketHandler

from .conf import config


logger = logging.getLogger('webapp')


class LogsterException(Exception):
    pass


class BaseHandler:
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


class BaseRequestHandler(BaseHandler, RequestHandler):
    pass


class BaseWebSocketHandler(BaseHandler, WebSocketHandler):
    pass


class IndexHandler(BaseRequestHandler):
    @gen.coroutine
    @authenticated
    def get(self):
        self.render('index.html')


class LoginHandler(BaseRequestHandler):
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


class LogoutHandler(BaseRequestHandler):
    @authenticated
    def get(self):
        self.clear_cookie('user')
        self.redirect('/')


_web_socket_pool = {}


class ClientWebSocketHandler(BaseWebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        user = self.get_secure_cookie('user')
        logger.info('Authenticated user "%s" started websocket connection',
                    user)

        self.log_name = self.get_argument('log')

        IOLoop.current().spawn_callback(self._process_new_websocket)

    @gen.coroutine
    def _process_new_websocket(self):
        try:
            entries = yield self._get_initial_log_entries(self.log_name)
        except LogsterException as e:
            self.write_message(json.dumps({
                'message_type': 'error',
                'error': str(e)
            }))

            self.added = False
            self.close()
            return

        self.write_message(json.dumps({
            'message_type': 'new_entries',
            'entries': entries
        }))

        if self.log_name not in _web_socket_pool:
            _web_socket_pool[self.log_name] = []

        _web_socket_pool[self.log_name].append(self)
        self.added = True

        logger.debug('Socket handler was added to the pool')

    @gen.coroutine
    def _get_initial_log_entries(self, log_name):
        log = yield self.db.logs.find_one({
            'name': log_name
        })

        if log is None:
            raise LogsterException('Log is not found')

        log_entries = yield self.db.entries.find({
            'log': log['_id']
        }).sort('order', pymongo.DESCENDING).limit(
            config['app']['initialLineCount']).to_list(None)

        return [{
            'content': e['content'],
            'order': e['order']
        } for e in reversed(log_entries)]

    def on_message(self, message):
        pass

    def on_close(self):
        if not self.added:
            return

        _web_socket_pool[self.log_name].remove(self)

        logger.debug('Socket handler was removed from the pool (token={})',
                     self.token)

    def send_message(self, msg):
        self.write_message(json.dumps({'message': msg}))

        logger.debug('Message was sent (token=%s, msg="%s")',
                     self.token, msg)


class ScannerNotificationsHandler(BaseRequestHandler):
    @gen.coroutine
    def post(self):
        if self.request.remote_ip != '127.0.0.1':
            logger.info('Skip notifications from non-localhost (ipaddr=%s)',
                        self.request.remote_ip)
            return

        # Body format:
        # {
        #     "log_id": "<ObjectId hexstr>",
        #     "entry_ids": ["<ObjectId hexstr>", ...]
        # }
        body = self.json_body

        logger.info('Scanner notification received (body: %s)', body)

        self.log = yield self.db.logs.find_one({
            '_id': ObjectId(body['log_id'])
        })

        if self.log is None:
            logger.info('Log is not found, cannot process notification '
                        '(log_id=%s)', body['log_id'])
            return

        if self.log['name'] != config['app']['defaultLog']:
            # don't receive notfications from other locations than default
            logger.info('Skip notifications from non-default log '
                        '(log_name=%s)', self.log['name'])
            return

        self.entries = yield self.db.entries.find({
            '_id': {
                '$in': [ObjectId(ent) for ent in body['entry_ids']]
            }
        }).sort('order').to_list(None)

        websock_message = self._build_client_notif_message()

        # todo: fix error
        for _, v in _test_socket_pool.items():
            v.send_message(json.dumps())
            for ent in self.entries:
                v.send_message(ent['content'])

    def _build_client_notif_message(self):
        # todo
        return None
