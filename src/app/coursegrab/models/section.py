from app import db
from app.coursegrab.models.course import Course
from app.coursegrab.models.user import User


class Section(db.Model):
    __tablename__ = "sections"
    catalog_num = db.Column(db.Integer, primary_key=True)
    instructors = db.Column(db.String, nullable=True)
    mode = db.Column(db.String, nullable=True)
    section = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    def __init__(self, **kwargs):
        self.catalog_num = kwargs.get("catalog_num")
        self.instructors = kwargs.get("instructors")
        self.mode = kwargs.get("mode")
        self.section = kwargs.get("section")
        self.status = kwargs.get("status")
        self.course_id = kwargs.get("course_id")

    def serialize(self):
        course = Course.query.filter_by(id=self.course_id).first()
        return {
            "catalog_num": self.catalog_num,
            "course_num": course.course_num,
            "instructors": self.instructors.split(",") if self.instructors else [],
            "mode": self.mode,
            "title": course.title,
            "section": self.section,
            "status": self.status,
            "subject_code": course.subject_code,
        }

    # Adds `is_tracking` field
    def serialize_with_user(self, user_id):
        user = User.query.get(user_id)
        section = self.serialize()
        section["is_tracking"] = True if self in user.sections else False
        return section

    def __eq__(self, obj):
        return (
            isinstance(obj, Section)
            and obj.catalog_num == self.catalog_num
            and obj.section == self.section
            and obj.course_id == self.course_id
        )
