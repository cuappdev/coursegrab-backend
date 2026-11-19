from . import *
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from app.coursegrab.utils.api_error import APIError


REVIEW_EMAILS = {"appstoreappdev@gmail.com", "coursegrab.droid@gmail.com"}


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

    section.num_tracking += 1
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

    section.num_tracking -= 1
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


def get_or_create_firebase_user(claims):
    """Link once using verified email, then resolve by UID. Never reassign a UID."""
    uid = claims.get("uid")
    email = claims.get("email")
    if not isinstance(uid, str) or not uid or len(uid) > 128:
        raise APIError("Invalid Firebase identity.", 401)
    if claims.get("email_verified") is not True or not isinstance(email, str):
        raise APIError("A verified email address is required.", 403)
    email = email.strip().lower()
    local_part, _, domain = email.partition("@")
    if email.count("@") != 1 or not local_part or (domain != "cornell.edu" and email not in REVIEW_EMAILS):
        raise APIError("You must use a Cornell email.", 403)
    if claims.get("firebase", {}).get("sign_in_provider") != "google.com":
        raise APIError("Please sign in with Google.", 403)

    for attempt in range(2):
        try:
            user = User.query.filter_by(firebase_uid=uid).first()
            if user:
                if user.email != email:
                    user.email = email
                    db.session.commit()
                return user
            matches = User.query.filter(func.lower(User.email) == email).all()
            if len(matches) > 1 or (matches and matches[0].firebase_uid not in (None, uid)):
                raise APIError("Account identity conflict. Please contact support.", 409)
            if matches:
                user_id = matches[0].id
                # Compare-and-set prevents simultaneous sign-ins from replacing a link.
                changed = User.query.filter_by(id=user_id, firebase_uid=None).update(
                    {"firebase_uid": uid}, synchronize_session=False
                )
                db.session.commit()
                user = User.query.get(user_id)
                if not changed and user.firebase_uid != uid:
                    raise APIError("Account identity conflict. Please contact support.", 409)
                return user
            name = claims.get("name") or ""
            first_name, _, last_name = name.partition(" ")
            user = User(email=email, first_name=first_name, last_name=last_name, firebase_uid=uid)
            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            if attempt:
                raise APIError("Account identity conflict. Please contact support.", 409)
