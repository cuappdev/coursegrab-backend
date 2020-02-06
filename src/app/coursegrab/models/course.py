from app import db


class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    subject_code = db.Column(db.String, nullable=False)
    course_num = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String, nullable=False)
    sections = db.relationship("Section", cascade="delete")

    def __init__(self, **kwargs):
        self.subject_code = kwargs.get("subject_code")
        self.course_num = kwargs.get("course_num")
        self.title = kwargs.get("title")

    def serialize(self):
        return {
            "subject_code": self.subject_code,
            "course_num": self.course_num,
            "title": self.title,
            "sections": [section.serialize() for section in self.sections],
        }
