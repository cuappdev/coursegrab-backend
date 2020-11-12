from app import db


users_to_sections = db.Table(
    "users_to_sections",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("catalog_num", db.Integer, db.ForeignKey("sections.catalog_num")),
)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.Integer, nullable=False)
    notification = db.Column(db.String, nullable=True)

    sections = db.relationship("Section", secondary=users_to_sections, backref="users")
    sessions = db.relationship("Session", back_populates="user", cascade="all, delete")

    def __init__(self, **kwargs):
        self.email = kwargs.get("email")
        self.first_name = kwargs.get("first_name")
        self.last_name = kwargs.get("last_name")
        self.notification = None  # Default notifications set to None

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "notification": self.notification,
        }
