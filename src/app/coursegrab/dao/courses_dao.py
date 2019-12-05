from . import *


def get_course_by_catalog_num(catalog_num):
    return Course.query.get(catalog_num)


def create_courses(course_lst):
    for (subject_code, course_num, title, catalog_num, section) in course_lst:
        course = Course(
            subject_code=subject_code, course_num=course_num, title=title, catalog_num=catalog_num, section=section
        )
        db.session.add(course)
    db.session.commit()
    return course_lst
