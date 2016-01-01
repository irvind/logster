import os

from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.httpserver import HTTPServer

from motor.motor_tornado import MotorClient

from . import handlers
from .conf import config


class LogsterApplication(Application):
    handlers = [
        (r'/', handlers.IndexHandler),
        (r'/login', handlers.LoginHandler),
        (r'/logout', handlers.LogoutHandler),
    ]

    settings = {
        'template_path': os.path.join(
            os.path.dirname(__file__), '../templates'),
        'cookie_secret': config['app']['secret'],
        'login_url': '/login',
    }

    def __init__(self):
        db = self._connect_to_db()

        super(LogsterApplication, self).__init__(
            handlers=self.handlers,
            db=db,
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

        db = getattr(self.db_client, db_conf['dbName'])

        return db


def run_server():
    app = LogsterApplication()
    server = HTTPServer(app)
    server.listen(config['app']['port'])

    IOLoop.current().start()
