import datetime
import hashlib
import os
from app import db


users_to_courses = db.Table(
    "users_to_courses",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("course_id", db.Integer, db.ForeignKey("courses.catalog_num")),
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

    courses = db.relationship("Course", secondary=users_to_courses, backref="users")

    def __init__(self, **kwargs):
        self.email = kwargs.get("email")
        self.first_name = kwargs.get("first_name")
        self.last_name = kwargs.get("last_name")
        self.courses = db.relationship("Course", secondary=users_to_courses, backref="users")
        self.refresh_session()

    def generate_token(self):
        return hashlib.sha1(os.urandom(64)).hexdigest()

    def refresh_session(self):
        self.session_token = self.generate_token()
        self.session_expiration = datetime.datetime.now() + datetime.timedelta(days=1)
        self.update_token = self.generate_token()

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "session_token": self.session_token,
            "session_expiration": self.session_expiration,
            "update_token": self.update_token,
        }
