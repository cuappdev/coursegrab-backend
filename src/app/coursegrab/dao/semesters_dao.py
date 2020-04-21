from . import *


def get_current_semester():
    semester = Semester.query.first()
    return semester.current_semester if semester else None


def update_current_semester(current_semester):
    tracking_semester = Semester.query.first()
    if tracking_semester:
        db.session.delete(tracking_semester)

    new_semester = Semester(current_semester=current_semester)
    db.session.add(new_semester)
    db.session.commit()
