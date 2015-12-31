from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.httpserver import HTTPServer


class LogsterApplication(Application):
    handlers = []
    settings = {}

    def __init__(self):
        super(LogsterApplication, self).__init__(
            handlers=self.handlers,
            **self.settings
        )


def run_server():
    app = LogsterApplication()
    server = HTTPServer(app)
    server.listen(8888)

    IOLoop.current().start()
