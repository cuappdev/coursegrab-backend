import datetime
import hashlib
import os
from app import db


users_to_sections = db.Table(
    "users_to_courses",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("section_id", db.Integer, db.ForeignKey("sections.catalog_num")),
)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.Integer, nullable=False)

    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)
    update_token = db.Column(db.String, nullable=False, unique=True)

    is_ios = db.Column(db.Boolean, nullable=True)
    device_token = db.Column(db.String, nullable=True)

    sections = db.relationship("Section", secondary=users_to_sections, backref="users")

    def __init__(self, **kwargs):
        self.email = kwargs.get("email")
        self.first_name = kwargs.get("first_name")
        self.last_name = kwargs.get("last_name")
        self.refresh_session()

    def generate_token(self):
        return hashlib.sha1(os.urandom(64)).hexdigest()

    def refresh_session(self):
        self.session_token = self.generate_token()
        self.session_expiration = datetime.datetime.now() + datetime.timedelta(days=1)
        self.update_token = self.generate_token()

    def serialize(self):
        return {
            **self.serialize_session(),
            "id": self.id,
            "device_token": self.device_token,
            "email": self.email,
            "first_name": self.first_name,
            "is_ios": self.is_ios,
            "last_name": self.last_name,
        }

    def serialize_session(self):
        return {
            "session_token": self.session_token,
            "session_expiration": round(self.session_expiration.timestamp()),
            "update_token": self.update_token,
        }
