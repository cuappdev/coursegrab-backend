import json
import jwt
import time
from hyper import HTTP20Connection
from constants import ALGORITHM
from os import environ

key_id = environ["APNS_KEY_ID"]
auth_key_path = environ["APNS_AUTH_KEY_PATH"]
team_id = environ["APNS_TEAM_ID"]
bundle_id = environ["APNS_BUNDLE_ID"]
apn_url = "api.sandbox.push.apple.com:443" if environ["FLASK_ENV"] == "development" else "api.push.apple.com:443"

f = open(auth_key_path)
auth_key = f.read()
f.close()


def send_notifications(device_tokens):
    token = jwt.encode(
        {"iss": team_id, "iat": time.time()}, auth_key, algorithm=ALGORITHM, headers={"alg": ALGORITHM, "kid": key_id},
    )

    request_headers = {
        "apns-expiration": "0",
        "apns-priority": "10",
        "apns-topic": bundle_id,
        "authorization": "bearer {0}".format(token.decode("ascii")),
    }

    payload_data = {
        "aps": {"alert": "Hello", "sound": "default"},
    }
    payload = json.dumps(payload_data).encode("utf-8")

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

    if not successful_tokens:  # No successful push notification
        raise Exception("IOS: Failure to deliver message to all devices")
