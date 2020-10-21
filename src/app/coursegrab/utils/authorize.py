from functools import wraps
from flask import request
from app.coursegrab.dao.sessions_dao import verify_session


def extract_bearer(f):
    @wraps(f)
    def inner(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if auth_header is None:
            raise Exception("Missing authorization header.")
        bearer_token = auth_header.replace("Bearer ", "").strip()
        if not bearer_token:
            raise Exception("Invalid authorization header.")
        return f(bearer_token=bearer_token, *args, **kwargs)

    return inner


def authorize_user(f):
    @wraps(f)
    @extract_bearer
    def inner(*args, **kwargs):
        session_token = kwargs.get("bearer_token")
        user, session = verify_session(session_token)
        return f(user=user, session=session, *args, **kwargs)

    return inner
