from . import *


class RetrieveTrackingController(AppDevController):
    def get_path(self):
        return "/users/tracking/"

    def get_methods(self):
        return ["GET"]

    @authorize_user
    def content(self, **kwargs):
        user = kwargs.get("user")
        courses = users_dao.get_tracked_courses(user.id)
        return [course.serialize() for course in courses]
