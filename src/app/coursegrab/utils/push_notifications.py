import json
import jwt
import time
from app.coursegrab.utils.constants import ALGORITHM, ANDROID, IPHONE
from hyper import HTTP20Connection
from firebase_admin import initialize_app, messaging
from os import environ

from app.coursegrab.dao.sections_dao import get_users_tracking_section

f = open(environ["APNS_AUTH_KEY_PATH"])
auth_key = f.read()
f.close()

firebase_app = initialize_app()


def notify_users(section):
    users = get_users_tracking_section(section.catalog_num)

    android_tokens = []
    ios_tokens = []

    for user in users:
        if user.notification == ANDROID:
            android_tokens.append(user.device_token)
        elif user.notification == IPHONE:
            ios_tokens.append(user.device_token)

    if android_tokens:
        send_android_notification(android_tokens, section.serialize())
    if ios_tokens:
        send_ios_notification(ios_tokens, section.serialize())


def send_ios_notification(device_tokens, payload_data):
    token = jwt.encode(
        {"iss": environ["APNS_TEAM_ID"], "iat": time.time()},
        auth_key,
        algorithm=ALGORITHM,
        headers={"alg": ALGORITHM, "kid": environ["APNS_KEY_ID"]},
    )

    request_headers = {
        "apns-expiration": "0",
        "apns-priority": "10",
        "apns-topic": environ["APNS_BUNDLE_ID"],
        "authorization": "bearer {0}".format(token.decode("ascii")),
    }

    payload_data = {"aps": {"alert": json.dumps(payload_data)}}
    payload = json.dumps(payload_data).encode("utf-8")

    apn_url = "api.sandbox.push.apple.com:443" if environ["FLASK_ENV"] == "development" else "api.push.apple.com:443"
    conn = HTTP20Connection(apn_url, force_proto="h2")

    successful_tokens = []
    for token in device_tokens:
        try:
            path = "/3/device/%s" % (token)
            conn.request("POST", path, payload, headers=request_headers)
            resp = conn.get_response()
            if resp.status == 200:
                successful_tokens.append(token)
        except:
            pass

    print("iOS : {0} messages sent successfully out of {1}".format(len(successful_tokens), len(device_tokens)))
    return len(successful_tokens)


def send_android_notification(device_tokens, payload):
    message = messaging.MulticastMessage(data={"message": json.dumps(payload)}, tokens=device_tokens)
    response = messaging.send_multicast(message)
    print("Android : {0} messages sent successfully out of {1}".format(response.success_count, len(device_tokens)))
    return response.success_count
