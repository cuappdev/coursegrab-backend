from . import *


def get_course_by_subject_and_course_num(subject_code, course_num):
    return Course.query.filter_by(subject_code=subject_code, course_num=course_num).first()


def create_course(subject_code, course_num, title):
    optional_course = get_course_by_subject_and_course_num(subject_code, course_num)

    if optional_course:
        return optional_course

    course = Course(subject_code=subject_code, course_num=course_num, title=title)
    db.session.add(course)
    db.session.commit()
    return course
