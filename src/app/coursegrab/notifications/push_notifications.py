import json
import jwt
import time
import base64
import os
from app.coursegrab.utils.constants import ALGORITHM, ANDROID, EMAIL, IOS, COURSEGRAB_EMAIL, MAX_BCC_SIZE
from datetime import datetime
from hyper import HTTP20Connection
from firebase_admin import initialize_app, messaging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *

from app.coursegrab.dao.sections_dao import get_users_tracking_section
from app.coursegrab.dao.sessions_dao import delete_session_expired_device_tokens
from app.coursegrab.dao.users_dao import get_user_device_tokens

# Initialize APNS
try:
    f = open(os.environ["APNS_AUTH_KEY_PATH"])
    auth_key = f.read()
    f.close()
except:
    print("Error initializing APNS")

# Initialize FCM
firebase_app = initialize_app()

# Initialize SendGrid client
try:
    sendgrid_client = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
except:
    print("Error initializing SendGrid")

# Initialize email body
try:
    f = open(os.path.join(os.path.dirname(__file__), 'message.html'), "r")
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
            # always send email
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
        {"iss": os.environ["APNS_TEAM_ID"], "iat": time.time()},
        auth_key,
        algorithm=ALGORITHM,
        headers={"alg": ALGORITHM, "kid": os.environ["APNS_KEY_ID"]},
    )

    request_headers = {
        "apns-expiration": "0",
        "apns-priority": "10",
        "apns-topic": os.environ["APNS_BUNDLE_ID"],
        "authorization": "bearer {0}".format(token),
    }

    payload_data = {"aps": {"alert": payload_data, "badge": 1}}
    payload = json.dumps(payload_data).encode("utf-8")

    apn_url = "api.sandbox.push.apple.com:443" if os.environ["FLASK_ENV"] == "development" else "api.push.apple.com:443"
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
    subject_code = serialized_section['subject_code']
    course_num = serialized_section['course_num']
    end_section_index = serialized_section["section"].find("/")
    trimmed_section_name = serialized_section["section"][:end_section_index].strip()

    # SendGrid has a limit of 1000 total recipients (to + cc + bcc) per request. 
    # We have to use up 1 out of 1000 to send the email to ourselves. Thus we have 999 emails left to fill up with user's emails
    # in the bcc section. So we partition the emails into chunks of size 999 max. (e.g. email_chunks = [ [999 emails], [21 emails] ])
    email_chunks = [emails[ind:ind + MAX_BCC_SIZE] for ind in range(0, len(emails), MAX_BCC_SIZE)]

    try:
        # Send separate email for each chunk
        for chunk in email_chunks:
            send_single_email(subject_code, course_num, trimmed_section_name, chunk)
    except Exception as e:
        print("Error while sending email notifications:", e)


def send_single_email (subject_code, course_num, trimmed_section_name, email_chunk):
    """Send email notification to single chunk of user emails (max 999 bcc emails)"""
    course_name_full = f"{subject_code} {course_num} {trimmed_section_name}"
    message = Mail(
        from_email=(COURSEGRAB_EMAIL, "CourseGrab by AppDev"),
        to_emails=COURSEGRAB_EMAIL, # Send to ourselves
        subject=f"{course_name_full} is Now Open",
        html_content=email_body.replace("COURSE_NAME_NUM", course_name_full),
    )

    personalization = Personalization()
    for bcc_email in email_chunk:                     # Add users' emails to bcc
        personalization.add_bcc(Email(bcc_email))

    message.add_personalization(personalization)

    try:
        sendgrid_client.send(message)
    except Exception as e:
        print(f"Error sending email: {e.message}")
    