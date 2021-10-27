from . import *
from ..utils.constants import NUM_SEARCH_RESULT


def get_course_by_id(course_id):
    return Course.query.filter_by(id=course_id).first()


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

def search_courses(query):
    results = Course.query.filter(Course.search_string.ilike("%{}%".format(query))).limit(NUM_SEARCH_RESULT)
    results = sorted(results, key = lambda r : find_query_index(r, query))
    return results


def find_query_index(course, key):
    try: 
        return course.search_string.lower().index(key.lower()) 
    except(ValueError): 
        return -1

def clear_table():
    Course.query.delete()
