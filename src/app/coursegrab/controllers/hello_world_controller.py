from . import *


class HelloWorldController(AppDevController):
    def get_path(self):
        return "/hello/"

    def get_methods(self):
        return ["GET"]

    @authorize_user
    def content(self, **kwargs):
        return {"message": "Hello, world!"}
