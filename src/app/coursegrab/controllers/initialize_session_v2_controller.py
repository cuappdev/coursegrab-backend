from os import environ
from google.auth.transport import requests
from google.oauth2 import id_token
from . import *
from ..utils.constants import IOS


class InitializeSessionV2Controller(AppDevController):
    def get_path(self):
        return "/session/initialize/v2/"

    def get_methods(self):
        return ["POST"]

    def content(self, **kwargs):
        data = request.get_json()
        token = data.get("token")
        device_type = data.get("device_type")
        device_token = data.get("device_token")
        given_name = data.get("given_name")
        family_name = data.get("family_name")
        try:
            if device_type == IOS:
                client_id = environ["IOS_CLIENT_ID"]
            else:  # device_type is ANDROID or WEB
                client_id = environ["FIREBASE_CLIENT_ID"]
            
            id_info = id_token.verify_oauth2_token(token, requests.Request(), client_id)
            if id_info["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
                raise ValueError("Wrong issuer.")

            # ID token is valid. Get the user's Google Account information.
            email, first_name, last_name = id_info.get("email"), id_info.get("given_name", given_name), id_info.get("family_name", family_name)
            if email != "coursegrabappstore@gmail.com" and email[email.find("@") + 1 :] != "cornell.edu":
                raise Exception("You must use a Cornell email")

            user = users_dao.create_user(email, first_name, last_name) # Default notification mode = EMAIL
            session = sessions_dao.create_session(user.id, device_type, device_token)
            return session.serialize_session_v2()

        except ValueError:
            raise Exception("Invalid token")
