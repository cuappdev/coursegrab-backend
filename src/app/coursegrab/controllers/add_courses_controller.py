from . import *
from app.coursegrab.utils import scraper


class AddCoursesController(AppDevController):
    def get_path(self):
        return "/courses/add/"

    def get_methods(self):
        return ["POST"]

    @authorize_user
    def content(self, **kwargs):
        courses = scraper.scrape_classes()
        courses = courses_dao.create_courses(courses)
        return [course.serialize() for course in courses]
