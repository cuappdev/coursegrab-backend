from flask import Flask, redirect, request
import os
import requests
from urllib.parse import urlencode

app = Flask(__name__)


@app.route("/")
@app.route("/login/")
def login():
    params = {
        "client_id": os.environ["CLIENT_ID"],
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": "http://localhost:5000/oauth2callback",
        "hd": "cornell.edu",
    }
    return redirect("https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params))


@app.route("/oauth2callback")
def callback():
    token_res = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": request.args["code"],
            "client_id": os.environ["CLIENT_ID"],
            "client_secret": os.environ["CLIENT_SECRET"],
            "redirect_uri": "http://localhost:5000/oauth2callback",
            "grant_type": "authorization_code",
        },
    )
    if not token_res.ok:
        return token_res.json()
    access_token = token_res.json()["access_token"]
    person_res = requests.get(
        "https://people.googleapis.com/v1/people/me",
        headers={"Authorization": "Bearer " + access_token},
        params={"personFields": "names,emailAddresses"},
    )
    return person_res.json()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ["PORT"])
