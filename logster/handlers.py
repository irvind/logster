import random

from tornado import gen
from tornado.web import RequestHandler, authenticated
from tornado.websocket import WebSocketHandler


class BaseHandler(RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        return self.get_secure_cookie('user')


class IndexHandler(BaseHandler):
    @authenticated
    def get(self):
        context = {
            'log_entries': ['Entity 1', 'Entity 2', 'Entity 3'],
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


class TestSocketHandler(WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        token = self.get_argument('token')
        self.write_message(token)

    def on_message(self, message):
        pass

    def on_close(self):
        pass
