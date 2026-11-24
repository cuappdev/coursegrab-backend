from datetime import datetime

from sqlalchemy.exc import IntegrityError

from app import db
from app.coursegrab.models.device_registration import DeviceRegistration
from app.coursegrab.models.session import Session
from app.coursegrab.utils.api_error import APIError
from app.coursegrab.utils.constants import ANDROID, IOS


def register_new_device(user_id, data):
    device_type, token = _validate_device_data(data)
    registration = DeviceRegistration.query.filter_by(device_type=device_type, device_token=token).first()
    if registration is not None and registration.user_id != user_id:
        raise APIError("Device is registered to another account. Unregister it before switching accounts.", 409)
    if registration is None:
        registration = DeviceRegistration(user_id=user_id)
    return _save_registration(registration, device_type, token)


def update_device_registration(user_id, registration_id, data):
    device_type, token = _validate_device_data(data)
    registration_by_id = owned_device(user_id, registration_id)
    registration_by_token = DeviceRegistration.query.filter_by(device_type=device_type, device_token=token).first()
    if registration_by_token is not None:
        if registration_by_token.user_id != user_id:
            raise APIError("Device is registered to another account. Unregister it before switching accounts.", 409)
        if registration_by_token.id != registration_by_id.id:
            raise APIError("Token already belongs to another registration.", 409)

    # Clear matching legacy copies so rotation cannot revive old notifications.
    if registration_by_id.device_token and (
        registration_by_id.device_token != token or registration_by_id.device_type != device_type
    ):
        Session.query.filter_by(
            user_id=user_id, device_type=registration_by_id.device_type, device_token=registration_by_id.device_token
        ).update({"device_token": None}, synchronize_session=False)
    return _save_registration(registration_by_id, device_type, token)


def _validate_device_data(data):
    if not isinstance(data, dict):
        raise APIError("Expected a JSON object.", 400)
    device_type = data.get("device_type")
    token = data.get("device_token")
    if device_type not in (IOS, ANDROID):
        raise APIError("device_type must be IOS or ANDROID.", 400)
    if not isinstance(token, str) or not token.strip() or len(token) > 4096:
        raise APIError("A nonempty device_token is required (maximum 4096 characters).", 400)
    return device_type, token


def _save_registration(registration, device_type, token):
    registration.device_type = device_type
    registration.device_token = token
    registration.updated_at = datetime.utcnow()
    db.session.add(registration)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise APIError("Device registration conflict. Please retry.", 409)
    return registration


def owned_device(user_id, registration_id):
    registration = DeviceRegistration.query.filter_by(id=registration_id, user_id=user_id).first()
    if registration is None:
        raise APIError("Device registration not found.", 404)
    return registration


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
