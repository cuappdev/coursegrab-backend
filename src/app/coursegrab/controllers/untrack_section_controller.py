from . import *


class UntrackSectionController(AppDevController):
    def get_path(self):
        return "/sections/untrack/"

    def get_methods(self):
        return ["POST"]

    @authorize_user
    def content(self, **kwargs):
        data = request.get_json()
        user = kwargs.get("user")
        catalog_num = data.get("course_id")
        if not catalog_num:
            raise Exception("Must provide catalog number.")

        section = users_dao.untrack_section(user.id, catalog_num)
        return section.serialize_with_user(user.id)
