import datetime
from . import *


def get_session_by_id(id):
    return Session.query.get(id)


def get_user_from_session(session):
    user = session.serialize()["user"]
    if not user:
        raise Exception("User does not exist.")
    return user


# If there is information about device_token and there exists a valid session for it,
# refresh that session since we can identify the device. Otherwise, create a new user session.
def create_session(user_id, device_type, device_token=None):
    if device_token:
        session = Session.query.filter(Session.device_token == device_token).first()
        if session:
            session.refresh_session()
            db.session.commit()
            return session
    session = Session(user_id=user_id, device_type=device_type, device_token=device_token)
    db.session.add(session)
    db.session.commit()
    return session


def verify_session(session_token):
    session = Session.query.filter(Session.session_token == session_token).first()
    if not session or datetime.datetime.now() > session.session_expiration:
        raise Exception("Invalid session token.")
    user = get_user_from_session(session)
    return user, session


def refresh_session(update_token):
    session = Session.query.filter(Session.update_token == update_token).first()
    if not session:
        raise Exception("Invalid update token.")
    session.refresh_session()
    db.session.commit()
    return session


def update_device_token(session_id, device_token):
    session = get_session_by_id(session_id)
    session.device_token = device_token
    db.session.add(session)
    db.session.commit()
    return session


# If there is an expired device_token, it is no longer in use (probably because the user
# deleted the app). Therefore, we no longer need a session associated with this device_token.
def delete_session_expired_device_tokens(tokens):
    for token in tokens:
        Session.query.filter(Session.device_token == token).delete()
    db.session.commit()
