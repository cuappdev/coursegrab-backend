from app.coursegrab.utils.base_controller import abc, BaseController
from flask import redirect

# A REST-API controller that handles boilerplate for
# redirecting
class AppDevRedirectController(BaseController):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def make_uri(self, **kwargs):
        return ""  # URI to redirect to

    def get_name(self):
        return self.get_path().replace("/", "-")

    def response(self, **kwargs):
        uri = self.make_uri(**kwargs)
        return redirect(uri, code=302)
