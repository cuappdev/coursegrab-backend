from . import *


def get_course_by_catalog_num(catalog_num):
    return Course.query.get(catalog_num)


def get_subject_by_catalog_num(catalog_num):
    course = get_course_by_catalog_num(catalog_num)
    if not course:
        raise Exception("Catalog number is invalid.")
    return course.subject_code


def create_courses(course_lst):
    courses = []
    for (subject_code, course_num, title, catalog_num, section) in course_lst:
        course = Course(
            subject_code=subject_code, course_num=course_num, title=title, catalog_num=catalog_num, section=section
        )
        db.session.add(course)
        courses.append(course)
    db.session.commit()
    return courses
