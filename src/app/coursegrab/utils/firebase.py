import os
from threading import Lock

import firebase_admin
from firebase_admin import auth, exceptions

from app.coursegrab.utils.api_error import APIError

_initialization_lock = Lock()


def get_firebase_app():
    """Share the default Admin app between authentication and messaging."""
    with _initialization_lock:
        try:
            return firebase_admin.get_app()
        except ValueError:
            project_id = os.environ.get("FIREBASE_PROJECT_ID")
            options = {"projectId": project_id} if project_id else None
            return firebase_admin.initialize_app(options=options)


def verify_firebase_token(token):
    # Configuration failures must not be mistaken for invalid client credentials.
    app = get_firebase_app()
    try:
        claims = auth.verify_id_token(token, app=app, check_revoked=True)
        # Admin 4.0.1 checks revocation but does not reject disabled users itself.
        # Keep this explicit lookup until a separately tested SDK upgrade.
        if auth.get_user(claims["uid"], app=app).disabled:
            raise APIError("This account has been disabled.", 401)
        return claims
    except (auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserNotFoundError):
        raise APIError("Invalid or expired Firebase ID token. Please sign in again.", 401)
    except exceptions.FirebaseError:
        raise APIError("Authentication service unavailable. Please try again later.", 503)
