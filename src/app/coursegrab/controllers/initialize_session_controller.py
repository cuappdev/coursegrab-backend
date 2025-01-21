from os import environ

from google.auth.transport import requests
from google.oauth2 import id_token

from ..utils.constants import ANDROID, IOS
from . import *


class InitializeSessionController(AppDevController):
    def get_path(self):
        return "/session/initialize/"

    def get_methods(self):
        return ["POST"]

    def content(self, **kwargs):
        data = request.get_json()
        token = data.get("token")
        device_type = data.get("device_type")
        device_token = data.get("device_token")
        notification = None  # temporary fix
        try:
            if device_type == IOS:
                client_id = environ["IOS_CLIENT_ID"]
                notification = IOS  # temporary fix
            elif device_type == ANDROID:
                client_id = environ["ANDROID_CLIENT_ID"]
                notification = ANDROID  # temporary fix
            else:  # device_type == WEB
                client_id = None
            id_info = id_token.verify_oauth2_token(token, requests.Request(), client_id)

            if id_info["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
                raise ValueError("Wrong issuer.")
            # ID token is valid. Get the user's Google Account information.
            email, first_name, last_name = id_info.get("email"), id_info.get(
                "given_name", ""), id_info.get("family_name", "")
            if email != "coursegrab.droid@gmail.com" and email != "appstoreappdev@gmail.com" and email[email.find("@") + 1 :] != "cornell.edu":
                raise Exception("You must use a Cornell email")

            user = users_dao.create_user(email, first_name, last_name)
            session = sessions_dao.create_session(user.id, device_type, device_token)
            user = users_dao.update_notification(user.id, notification)  # temporary fix
            return session.serialize_session()

        except ValueError:
            raise Exception("Invalid token")
