from . import *


class RetrieveTrackingController(AppDevController):
    def get_path(self):
        return "/users/tracking/"

    def get_methods(self):
        return ["GET"]

    @authorize_user
    def content(self, **kwargs):
        user = kwargs.get("user")
        sections = users_dao.get_tracked_sections(user.id)
        return {"sections": [section.serialize_with_user(user.id) for section in sections]}
