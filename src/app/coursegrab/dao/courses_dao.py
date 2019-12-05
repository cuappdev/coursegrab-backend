from . import *
from app.coursegrab.utils import scraper


def get_course_by_catalog_num(catalog_num):
    return Course.query.get(catalog_num)


def get_subject_by_catalog_num(catalog_num):
    course = Course.query.filter(Course.catalog_num == catalog_num).first()
    if not course:
        raise Exception("Catalog number is invalid")
    return course.subject_code


def get_course_status_by_catalog_num(catalog_num):
    subject_code = get_subject_by_catalog_num(catalog_num)
    return scraper.get_course_status(subject_code, catalog_num)


def create_courses(course_lst):
    for (subject_code, course_num, title, catalog_num, section) in course_lst:
        course = Course(
            subject_code=subject_code, course_num=course_num, title=title, catalog_num=catalog_num, section=section
        )
        db.session.add(course)
    db.session.commit()
    return course_lst
