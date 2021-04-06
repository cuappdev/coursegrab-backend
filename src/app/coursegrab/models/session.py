import datetime
import hashlib
import os
from app import db


class Session(db.Model):
    __tablename__ = "sessions"
    id = db.Column(db.Integer, primary_key=True)
    device_token = db.Column(db.String, nullable=True)
    device_type = db.Column(db.String, nullable=True)

    last_used = db.Column(db.DateTime, nullable=False)
    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)
    update_token = db.Column(db.String, nullable=False, unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    user = db.relationship("User", back_populates="sessions")

    def __init__(self, **kwargs):
        self.device_token = kwargs.get("device_token")
        self.device_type = kwargs.get("device_type")
        self.user_id = kwargs.get("user_id")
        self.refresh_session()

    def generate_token(self):
        return hashlib.sha1(os.urandom(64)).hexdigest()

    def refresh_session(self):
        self.session_token = self.generate_token()
        self.session_expiration = datetime.datetime.now() + datetime.timedelta(days=1)
        self.update_token = self.generate_token()
        self.last_used = datetime.datetime.now()

    def serialize(self):
        return {
            **self.serialize_session(),
            "id": self.id,
            "device_token": self.device_token,
            "device_type": self.device_type,
            "user_id": self.user_id,
            "user": self.user,
            "last_used": round(self.last_used.timestamp())
        }

    def serialize_session(self):
        return {
            "session_token": self.session_token,
            "session_expiration": round(self.session_expiration.timestamp()),
            "update_token": self.update_token
        }
