from app import db
from models.course import Course


def get_course_by_id(id):
    return Course.query.get(id)


def get_course_by_catalog_num(catalog_num):
    return Course.query.filter(Course.catalog_num == catalog_num).first()


def create_courses(course_lst):
    for (subject_code, course_num, title, catalog_num, section) in course_lst:
        course = Course(
            subject_code=subject_code, course_num=course_num, title=title, catalog_num=catalog_num, section=section
        )
        db.session.add(course)
    db.session.commit()
    return course_lst
