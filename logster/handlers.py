from tornado.web import RequestHandler, authenticated


class BaseHandler(RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie('user')


class IndexHandler(BaseHandler):
    @authenticated
    def get(self):
        self.render('index.html')


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        # todo: auth user
        self.set_secure_cookie('user', self.get_argument('name'))
        self.redirect('/')


class LogoutHandler(BaseHandler):
    @authenticated
    def get(self):
        self.clear_cookie('user')
        self.redirect('/')
