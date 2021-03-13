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
from app.coursegrab.dao.sessions_dao import delete_session_expired_device_tokens
from app.coursegrab.dao.users_dao import get_user_device_tokens

try:
    f = open(environ["APNS_AUTH_KEY_PATH"])
    auth_key = f.read()
    f.close()
except:
    pass

firebase_app = initialize_app()


def notify_users(section):
    print(f"Sending notifications for section with catalog number: {section.catalog_num}")
    try:
        users = get_users_tracking_section(section.catalog_num)
        print(f"NOTIFICATIONS : {len(users)} users tracking {section.catalog_num}")

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

    title = (
        f"{serialized_section['subject_code']} {serialized_section['course_num']} {trimmed_section_name} is Now Open"
    )
    response = {
        "section": serialized_section,
        "timestamp": round(datetime.now().timestamp()),
        "title": title,
        "body": f"Class Nbr: {serialized_section['catalog_num']}. Grab your spot right now!",
    }
    return response


def send_ios_notification(device_tokens, payload_data):
    print(f"NOTIFICATIONS : Sending notifications to IOS users")

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
    expired_tokens = []
    for token in device_tokens:
        try:
            path = f"/3/device/{token}"
            conn.request("POST", path, payload, headers=request_headers)
            resp = conn.get_response()
            if resp.status == 200:
                successful_tokens.append(token)
            elif resp.status == 410:  # APNS status code for inactive device token
                expired_tokens.append(token)
        except:
            pass
    if expired_tokens:
        delete_session_expired_device_tokens(expired_tokens)

    print(f"iOS : {len(successful_tokens)} messages sent successfully out of {len(device_tokens)}")
    return len(successful_tokens)


def send_android_notification(device_tokens, payload):
    print(f"NOTIFICATIONS : Sending notifications to ANDROID users")

    successful_tokens = []
    expired_tokens = []

    for token in device_tokens:
        try:
            message = messaging.Message(data={"message": json.dumps(payload)}, token=token)
            response = messaging.send(message)
            if response:
                successful_tokens.append(token)
        except messaging.UnregisteredError:  # FCM Exception for invalid registration token (i.e. device token)
            expired_tokens.append(token)
        else:
            continue

    if expired_tokens:
        delete_session_expired_device_tokens(expired_tokens)

    print(f"Android : {len(successful_tokens)} messages sent successfully out of {len(device_tokens)}")
    return len(successful_tokens)


def send_emails(section, emails):
    print(f"NOTIFICATIONS : Sending notifications to EMAIL users")

    serialized_section = {**section.serialize(), "is_tracking": True}
    end_section_index = serialized_section["section"].find("/")
    trimmed_section_name = serialized_section["section"][:end_section_index].strip()

    f = open("./src/app/coursegrab/utils/message.html", "r")

    message = Mail(
        from_email=("mailer@coursegrab.me", "CourseGrab"),
        subject=f"{serialized_section['subject_code']} {serialized_section['course_num']} {trimmed_section_name} is Now Open",
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
