from app import db


users_to_courses = db.Table(
    "users_to_courses",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id"), primary_key=True),
)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.Integer, nullable=False)

    def __init__(self, **kwargs):
        self.email = kwargs.get("email")
        self.first_name = kwargs.get("first_name")
        self.last_name = kwargs.get("last_name")
        self.courses = db.relationship("Course", secondary=users_to_courses, backref="users")

    def serialize(self):
        return {"id": self.id, "email": self.email, "first_name": self.first_name, "last_name": self.last_name}
