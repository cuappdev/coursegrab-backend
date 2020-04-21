from app import db


class Semester(db.Model):
    __tablename__ = "semesters"
    current_semester = db.Column(db.String, primary_key=True)

    def __init__(self, **kwargs):
        self.current_semester = kwargs.get("current_semester")
