import os
import logging

from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.httpserver import HTTPServer

from . import handlers, base_dir
from .logging import setup_logging
from .conf import config
from .db import connect_to_db

logger = logging.getLogger('webapp')


class LogsterApplication(Application):
    handlers = [
        (r'/', handlers.IndexHandler),
        (r'/login', handlers.LoginHandler),
        (r'/logout', handlers.LogoutHandler),
        (r'/websock', handlers.ClientWebSocketHandler),
        (r'/notifications', handlers.ScannerNotificationsHandler),
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
        self.db_client, self.db = connect_to_db(async=True)

        super(LogsterApplication, self).__init__(
            handlers=self.handlers,
            **self.settings
        )


def run_server():
    setup_logging()

    app = LogsterApplication()
    server = HTTPServer(app)
    server.listen(config['app']['port'])

    logger.info('Logster started!')

    IOLoop.current().start()
