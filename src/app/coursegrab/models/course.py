from app import db


class Course(db.Model):
    __tablename__ = "courses"
    catalog_num = db.Column(db.Integer, primary_key=True)
    subject_code = db.Column(db.String, nullable=False)
    course_num = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String, nullable=False)
    section = db.Column(db.String, nullable=False)

    def __init__(self, **kwargs):
        self.catalog_num = kwargs.get("catalog_num")
        self.subject_code = kwargs.get("subject_code")
        self.course_num = kwargs.get("course_num")
        self.title = kwargs.get("title")
        self.section = kwargs.get("section")

    def serialize(self):
        return {
            "catalog_num": self.catalog_num,
            "subject_code": self.subject_code,
            "course_num": self.course_num,
            "title": self.title,
            "section": self.section,
        }
