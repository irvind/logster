from tornado.web import RequestHandler, authenticated


class BaseHandler(RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        return self.get_secure_cookie('user')


class IndexHandler(BaseHandler):
    @authenticated
    def get(self):
        self.render('index.html')


class LoginHandler(BaseHandler):
    def get(self):
        self._render_template()

    def post(self):
        # todo: auth user
        self.set_secure_cookie('user', self.get_argument('name'))
        self.redirect('/')

    def _render_template(self, error=''):
        self.render('login.html', error=error)


class LogoutHandler(BaseHandler):
    @authenticated
    def get(self):
        self.clear_cookie('user')
        self.redirect('/')
