from . import *
from app.coursegrab.utils import scraper


class AddCoursesController(AppDevController):
    def get_path(self):
        return "/courses/add/"

    def get_methods(self):
        return ["POST"]

    @authorize_user
    def content(self, **kwargs):
        catalog_tuples = scraper.scrape_classes()
        for course, sections in catalog_tuples:
            sections_dao.create_sections(course, sections)
