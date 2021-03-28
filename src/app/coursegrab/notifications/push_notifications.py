import json
import jwt
import time
import base64
from app.coursegrab.utils.constants import ALGORITHM, ANDROID, EMAIL, IOS, COURSEGRAB_EMAIL
from datetime import datetime
from hyper import HTTP20Connection
from firebase_admin import initialize_app, messaging
from os import environ, path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from email.mime.text import MIMEText

from . import *
from app.coursegrab.dao.sections_dao import get_users_tracking_section
from app.coursegrab.dao.sessions_dao import delete_session_expired_device_tokens
from app.coursegrab.dao.users_dao import get_user_device_tokens

# Initialize APNS
try:
    f = open(environ["APNS_AUTH_KEY_PATH"])
    auth_key = f.read()
    f.close()
except:
    print("Error initializing APNS")

# Initialize FCM
firebase_app = initialize_app()

# Initialize Gmail service
creds = None
if path.exists(environ["GMAIL_API_TOKEN"]): # Try reading token
    creds = Credentials.from_authorized_user_file(environ["GMAIL_API_TOKEN"], SCOPES)
if not creds or not creds.valid: # If there are no (valid) credentials available, try refreshing
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        print("Error initializing Gmail service")
gmail_service = build('gmail', 'v1', credentials=creds)
gmail_message = gmail_service.users().messages()

# Initialize email body
try:
    f = open("./src/app/coursegrab/notifications/message.html", "r")
    email_body = f.read()
    f.close()
except:
    print("Error getting email body")


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
            send_emails(section, emails)
    except Exception as e:
        print("Error while notifying users:", e)


def create_payload(section):
    """Creates notification payload for Android and iOS"""
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


def send_emails(section, emails):
    print(f"NOTIFICATIONS : Sending notifications to EMAIL users")

    serialized_section = {**section.serialize(), "is_tracking": True}
    end_section_index = serialized_section["section"].find("/")
    trimmed_section_name = serialized_section["section"][:end_section_index].strip()
    subject = f"{serialized_section['subject_code']} {serialized_section['course_num']} {trimmed_section_name} is Now Open"

    message = MIMEText(email_body, "html")
    message['to'] = COURSEGRAB_EMAIL        # Send to ourselves
    message['bcc'] = ",".join(emails)       # Add users' emails to bcc
    message['subject'] = subject

    gmail_body = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    gmail_message.send(userId="me", body=gmail_body).execute()
