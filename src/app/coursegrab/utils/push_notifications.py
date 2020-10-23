import json
import jwt
import time
from app.coursegrab.utils.constants import ALGORITHM, ANDROID, EMAIL, IOS
from datetime import datetime
from hyper import HTTP20Connection
from firebase_admin import initialize_app, messaging
from os import environ
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *

from app.coursegrab.dao.sections_dao import get_users_tracking_section
from app.coursegrab.dao.users_dao import get_user_device_tokens

try:
    f = open(environ["APNS_AUTH_KEY_PATH"])
    auth_key = f.read()
    f.close()
except:
    pass

firebase_app = initialize_app()


def notify_users(section):
    try:
        users = get_users_tracking_section(section.catalog_num)

        android_tokens = []
        ios_tokens = []
        emails = []

        for user in users:
            if user.notification == ANDROID:
                android_tokens.extend(get_user_device_tokens(user.id, ANDROID))
            elif user.notification == IOS:
                ios_tokens.extend(get_user_device_tokens(user.id, IOS))
            elif user.notification == EMAIL:
                emails.append(user.email)
        payload = create_payload(section)
        if android_tokens:
            send_android_notification(android_tokens, payload)
        if ios_tokens:
            send_ios_notification(ios_tokens, payload)
        if emails:
            send_emails(section.serialize(), emails)
    except Exception as e:
        print("Error while notifying users:", e)


def create_payload(section):
    serialized_section = {**section.serialize(), "is_tracking": True}

    end_section_index = serialized_section["section"].find("/")
    trimmed_section_name = serialized_section["section"][:end_section_index].strip()

    title = "{} {} {} is Now Open".format(
        serialized_section["subject_code"], serialized_section["course_num"], trimmed_section_name
    )
    response = {
        "section": serialized_section,
        "timestamp": round(datetime.now().timestamp()),
        "title": title,
        "body": "Open CourseGrab to log directly into Student Center and grab your spot!",
    }
    return response


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

    payload_data = {"aps": {"alert": payload_data, "badge": 1}}
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


def send_emails(section, emails):
    f = open("./src/app/coursegrab/utils/message.html", "r")

    message = Mail(
        from_email=("mailer@coursegrab.me", "CourseGrab"),
        subject="Course ID {0}: {1}, {2} is now open!".format(
            section["catalog_num"], section["title"], section["section"]
        ),
        html_content=f.read(),
    )

    personalization = Personalization()
    personalization.add_to(Email("mailer@coursegrab.me"))
    for bcc_email in emails:
        personalization.add_bcc(Email(bcc_email))

    message.add_personalization(personalization)

    try:
        sendgrid_client = SendGridAPIClient(environ.get("SENDGRID_API_KEY"))
        sendgrid_client.send(message)
    except Exception as e:
        print("Error while sending email notifications:", e)
