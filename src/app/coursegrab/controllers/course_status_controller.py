from . import *


class CourseStatusController(AppDevController):
    def get_path(self):
        return "/courses/<catalog_num>/status/"

    def get_methods(self):
        return ["GET"]

    @authorize_user
    def content(self, **kwargs):
        catalog_num = int(request.view_args.get("catalog_num"))
        status = courses_dao.get_course_status_by_catalog_num(catalog_num)
        if status == "invalid":
            raise Exception("Course was not found on registrar.")

        return status
