from . import *

class GetCourseByIDController(AppDevController):
    def get_path(self):
        return "/courses/<id>/"

    def get_methods(self):
        return ["GET"]

    @authorize_user_selective
    def content(self, **kwargs):
        user = kwargs.get("user")
        user_id = user.id if user else -1 

        course_id = int(request.view_args["id"])

        course = courses_dao.get_course_by_id(course_id)
        return course.serialize_with_user(user_id)
