from functools import wraps

from flask import request

from app.coursegrab.dao.sessions_dao import verify_session
from app.coursegrab.dao.users_dao import get_or_create_firebase_user
from app.coursegrab.utils.api_error import APIError
from app.coursegrab.utils.firebase import verify_firebase_token


def bearer_token():
    header = request.headers.get("Authorization")
    if header is None:
        raise APIError("Missing authorization header.", 401)
    parts = header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise APIError("Expected Authorization: Bearer <token>.", 401)
    return parts[1]


def extract_bearer(f):
    @wraps(f)
    def inner(*args, **kwargs):
        token = legacy_bearer_token()
        return f(*args, bearer_token=token, **kwargs)

    return inner


def legacy_bearer_token():
    # Existing SwiftUI releases send raw tokens instead of the Bearer scheme.
    header = request.headers.get("Authorization")
    if header is None:
        raise Exception("Missing authorization header.")
    token = header.replace("Bearer ", "").strip()
    if not token:
        raise Exception("Invalid authorization header.")
    return token


def authenticate():
    if request.blueprint == "coursegrab_v2":
        claims = verify_firebase_token(bearer_token())
        return {"user": get_or_create_firebase_user(claims)}
    token = legacy_bearer_token()
    user, session = verify_session(token)
    return {"user": user, "session": session, "bearer_token": token}


def authorize_user(f):
    @wraps(f)
    def inner(*args, **kwargs):
        kwargs.update(authenticate())
        return f(*args, **kwargs)

    return inner


def authorize_user_selective(f):
    @wraps(f)
    def inner(*args, **kwargs):
        header = request.headers.get("Authorization")
        if header is None:
            return f(*args, **kwargs)
        if request.blueprint == "coursegrab_v2":
            kwargs.update(authenticate())
        else:
            token = header.replace("Bearer ", "").strip()
            user, session = verify_session(token)
            kwargs.update(user=user, session=session)
        return f(*args, **kwargs)

    return inner
