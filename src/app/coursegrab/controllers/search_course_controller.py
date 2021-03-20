from . import *


class SearchCourseController(AppDevController):
    def get_path(self):
        return "/courses/search/"

    def get_methods(self):
        return ["POST"]

    def content(self, **kwargs):
        data = request.get_json()

        # Only try to access a user object if user's information is provided in the auth header
        # (web needs to allow searching even when user isn't logged in)
        user = kwargs.get("user")
        user_id = user.id if user else -1 

        query = data.get("query") if data else None
        if not query:
            raise Exception("Must provide query.")

        courses = courses_dao.search_courses(query.replace(" ", ""))
        return {"courses": [course.serialize_with_user(user_id) for course in courses], "query": query}
