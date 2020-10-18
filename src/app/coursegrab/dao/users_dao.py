from . import *


def get_user_by_id(id):
    return User.query.get(id)


def get_user_by_email(email):
    return User.query.filter(User.email == email).first()


def get_tracked_sections(user_id):
    return get_user_by_id(user_id).sections


def create_user(email, first_name, last_name):
    user = get_user_by_email(email)  # User credentials already exists
    if user:
        return user
    user = User(email=email, first_name=first_name, last_name=last_name)
    db.session.add(user)
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


# Get all device_tokens for a specific device_type
def get_user_device_tokens(user_id, device_type):
    user = get_user_by_id(user_id)
    tokens = []
    for session in user.sessions:
        if session.device_type == device_type and session.device_token:
            tokens.append(session.device_token)
    return tokens


def update_notification(user_id, notification):
    user = get_user_by_id(user_id)
    user.notification = notification
    db.session.add(user)
    db.session.commit()
    return user
