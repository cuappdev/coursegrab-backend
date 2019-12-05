from . import *


def get_user_by_id(id):
    return User.query.get(id)


def get_user_by_email(email):
    return User.query.filter(User.email == email).first()


def create_user(email, first_name, last_name):
    optional_user = get_user_by_email(email)

    if optional_user:
        return False, optional_user

    user = User(email=email, first_name=first_name, last_name=last_name)
    db.session.add(user)
    db.session.commit()
    return True, user


def add_course(user_id, catalog_num):
    user = get_user_by_id(user_id)
    course = courses_dao.get_course_by_catalog_num(catalog_num)

    if not course:
        raise Exception("Catalog number is not valid.")

    if course in user.courses:
        raise Exception("You are already tracking this course.")

    user.courses.append(course)
    db.session.commit()

    return course.serialize()
