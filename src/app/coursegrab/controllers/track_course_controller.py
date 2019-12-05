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

        user = users_dao.get_user_by_id(user_id)
        course = courses_dao.get_course_by_catalog_num(catalog_num)

        if not course:
            raise Exception("Catalog number is not valid.")

        if course in user.courses:
            raise Exception("You are already tracking this course.")

        user.courses.append(course)
        db.session.commit()

        return course.serialize()
