from os import environ
from urllib.parse import urlencode
from . import *


class LoginController(AppDevRedirectController):
    def get_path(self):
        return "/login/"

    def get_methods(self):
        return ["GET"]

    def make_uri(self, **kwargs):
        params = {
            "client_id": environ["CLIENT_ID"],
            "response_type": "code",
            "scope": "openid email profile",
            "redirect_uri": "http://localhost:5000/api/oauth2callback/",
            "hd": "cornell.edu",
        }
        return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
