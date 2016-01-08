import os
import logging.config

from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.httpserver import HTTPServer

from . import handlers, base_dir, setup_logging
from .conf import config, logging_conf
from .db import connect_to_db


class LogsterApplication(Application):
    handlers = [
        (r'/', handlers.IndexHandler),
        (r'/login', handlers.LoginHandler),
        (r'/logout', handlers.LogoutHandler),
        (r'/websock', handlers.TestSocketHandler),
        (r'/testtrigger', handlers.TestTriggerHandler),
        (r'/notifications', handlers.NotificationsHandler),
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

    IOLoop.current().start()
