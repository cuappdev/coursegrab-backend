from app.coursegrab.utils.appdev_controller import AppDevController
from app.coursegrab.utils.authorize import authorize_user


class CurrentUserController(AppDevController):
    def get_path(self):
        return "/users/me/"

    def get_methods(self):
        return ["GET"]

    @authorize_user
    def content(self, **kwargs):
        return {"user": kwargs["user"].serialize()}
