from . import *


class TrackCourseController(AppDevController):
    def get_path(self):
        return "/track_course/"

    def get_methods(self):
        return ["POST"]

    def content(self, **kwargs):
        data = request.get_json()
        user_id = data.get("user_id")
        catalog_num = data.get("course_id")

        if not (user_id and catalog_num):
            raise Exception("Missing required attributes.")

        return users_dao.add_course(user_id, catalog_num)
