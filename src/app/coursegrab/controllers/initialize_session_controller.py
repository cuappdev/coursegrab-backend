from os import environ
from google.auth.transport import requests
from google.oauth2 import id_token
from . import *
from app import db


class InitializeSessionController(AppDevController):
    def get_path(self):
        return "/session/initialize/"

    def get_methods(self):
        return ["POST"]

    def content(self, **kwargs):
        data = request.get_json()
        token = data.get("token")
        is_ios = data.get("is_ios")
        try:
            client_id = environ["IOS_CLIENT_ID"] if is_ios else environ["ANDROID_CLIENT_ID"]
            id_info = id_token.verify_oauth2_token(token, requests.Request(), client_id)

            if id_info["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
                raise ValueError("Wrong issuer.")

            # ID token is valid. Get the user's Google Account information.
            email, first_name, last_name = id_info["email"], id_info["given_name"], id_info["family_name"]
            created, user = users_dao.create_user(email, first_name, last_name)
            if not created:
                user.refresh_session()
                db.session.commit()

            return user.serialize_session()

        except ValueError:
            raise Exception("Invalid token")
