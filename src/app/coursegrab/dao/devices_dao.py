from datetime import datetime

from sqlalchemy.exc import IntegrityError

from app import db
from app.coursegrab.models.device_registration import DeviceRegistration
from app.coursegrab.models.session import Session
from app.coursegrab.utils.api_error import APIError
from app.coursegrab.utils.constants import ANDROID, IOS


def register_device(user_id, data, registration_id=None):
    if not isinstance(data, dict):
        raise APIError("Expected a JSON object.", 400)
    device_type = data.get("device_type")
    token = data.get("device_token")
    if device_type not in (IOS, ANDROID):
        raise APIError("device_type must be IOS or ANDROID.", 400)
    if not isinstance(token, str) or not token.strip() or len(token) > 4096:
        raise APIError("A nonempty device_token is required (maximum 4096 characters).", 400)
    device = None
    if registration_id is not None:
        device = owned_device(user_id, registration_id)
    existing = DeviceRegistration.query.filter_by(device_type=device_type, device_token=token).first()
    if existing and existing.user_id != user_id:
        raise APIError("Device is registered to another account. Unregister it before switching accounts.", 409)
    if device and existing and device.id != existing.id:
        raise APIError("Token already belongs to another registration.", 409)
    device = device or existing or DeviceRegistration(user_id=user_id)
    old_token, old_type = device.device_token, device.device_type
    device.device_type = device_type
    device.device_token = token
    device.updated_at = datetime.utcnow()
    db.session.add(device)
    # Clear matching legacy copies so rotation cannot revive old notifications.
    if old_token and (old_token != token or old_type != device_type):
        Session.query.filter_by(user_id=user_id, device_type=old_type, device_token=old_token).update(
            {"device_token": None}, synchronize_session=False
        )
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise APIError("Device registration conflict. Please retry.", 409)
    return device


def owned_device(user_id, registration_id):
    device = DeviceRegistration.query.filter_by(id=registration_id, user_id=user_id).first()
    if device is None:
        raise APIError("Device registration not found.", 404)
    return device


def unregister_device(user_id, registration_id):
    device = owned_device(user_id, registration_id)
    Session.query.filter_by(user_id=user_id, device_type=device.device_type, device_token=device.device_token).update(
        {"device_token": None}, synchronize_session=False
    )
    db.session.delete(device)
    db.session.commit()


def delete_expired_device_tokens(tokens, device_type):
    DeviceRegistration.query.filter(
        DeviceRegistration.device_type == device_type, DeviceRegistration.device_token.in_(tokens)
    ).delete(synchronize_session=False)
    Session.query.filter(Session.device_type == device_type, Session.device_token.in_(tokens)).delete(
        synchronize_session=False
    )
    db.session.commit()
