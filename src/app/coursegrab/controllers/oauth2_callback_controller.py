from os import environ
import requests
from . import *


class OAuth2CallbackController(AppDevController):
    def get_path(self):
        return "/oauth2callback/"

    def get_methods(self):
        return ["GET"]

    def content(self, **kwargs):
        if "error" in request.args:
            raise Exception("Failed to authenticate: " + request.args["error"])

        token_res = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": request.args["code"],
                "client_id": environ["CLIENT_ID"],
                "client_secret": environ["CLIENT_SECRET"],
                "redirect_uri": "http://localhost:5000/api/oauth2callback/",
                "grant_type": "authorization_code",
            },
        )
        token_json = token_res.json()
        if not token_res.ok:
            raise Exception("Error fetching token: " + token_json["error_description"])

        id_res = requests.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": token_json["id_token"]})
        id_json = id_res.json()
        if not id_res.ok:
            raise Exception("Error fetching token info: " + id_json["error_description"])

        created, user = users_dao.create_user(id_json["email"], id_json["given_name"], id_json["family_name"])
        return user.serialize()
