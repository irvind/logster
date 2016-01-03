import os

from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.httpserver import HTTPServer

from motor.motor_tornado import MotorClient

from . import handlers, base_dir
from .conf import config


class LogsterApplication(Application):
    handlers = [
        (r'/', handlers.IndexHandler),
        (r'/login', handlers.LoginHandler),
        (r'/logout', handlers.LogoutHandler),
        (r'/websock', handlers.TestSocketHandler),
    ]

    settings = {
        'template_path': os.path.join(base_dir, 'templates'),
        'cookie_secret': config['app']['secret'],
        'login_url': '/login',
        'static_path': os.path.join(base_dir, 'static'),
        'static_url_prefix': '/static/',
        'debug': True,
    }

    def __init__(self):
        self._connect_to_db()

        super(LogsterApplication, self).__init__(
            handlers=self.handlers,
            **self.settings
        )

    def _connect_to_db(self):
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
        self.db_client = MotorClient(conn_str)

        self.db = getattr(self.db_client, db_conf['dbName'])

        return self.db


def run_server():
    app = LogsterApplication()
    server = HTTPServer(app)
    server.listen(config['app']['port'])

    IOLoop.current().start()
