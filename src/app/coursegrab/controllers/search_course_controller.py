from . import *


class SearchCourseController(AppDevController):
    def get_path(self):
        return "/courses/search/"

    def get_methods(self):
        return ["POST"]

    @authorize_user
    def content(self, **kwargs):
        data = request.get_json()
        query = data.get("query")
        if not query:
            raise Exception("Must provide query.")

        courses = courses_dao.search_courses(query)
        return [course.serialize() for course in courses]
