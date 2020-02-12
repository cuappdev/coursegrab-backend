import datetime
from . import *


def get_user_by_id(id):
    return User.query.get(id)


def get_user_by_email(email):
    return User.query.filter(User.email == email).first()


def get_tracked_sections(user_id):
    return get_user_by_id(user_id).sections


def create_user(email, first_name, last_name):
    optional_user = get_user_by_email(email)
    if optional_user:
        return False, optional_user
    user = User(email=email, first_name=first_name, last_name=last_name)
    db.session.add(user)
    db.session.commit()
    return True, user


def verify_session(session_token):
    user = User.query.filter(User.session_token == session_token).first()
    if not user or datetime.datetime.now() > user.session_expiration:
        raise Exception("Invalid session token.")
    return user


def refresh_session(update_token):
    user = User.query.filter(User.update_token == update_token).first()
    if not user:
        raise Exception("Invalid update token.")
    user.refresh_session()
    db.session.commit()
    return user


def track_section(user_id, catalog_num):
    user = get_user_by_id(user_id)
    section = sections_dao.get_section_by_catalog_num(catalog_num)
    if not section:
        raise Exception("Catalog number is not valid.")
    if section in user.sections:
        raise Exception("You are already tracking this section.")

    user.sections.append(section)
    db.session.commit()
    return section


def untrack_section(user_id, catalog_num):
    user = get_user_by_id(user_id)
    section = sections_dao.get_section_by_catalog_num(catalog_num)
    if not section:
        raise Exception("Catalog number is not valid.")
    if section not in user.sections:
        raise Exception("You aren't tracking this section.")

    user.sections.remove(section)
    db.session.commit()
    return section
