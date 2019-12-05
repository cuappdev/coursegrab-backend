from flask import Blueprint
from app.coursegrab.controllers.course_status_controller import *
from app.coursegrab.controllers.create_user_controller import *
from app.coursegrab.controllers.hello_world_controller import *
from app.coursegrab.controllers.track_course_controller import *

# CourseGrab Blueprint
coursegrab = Blueprint("coursegrab", __name__, url_prefix="/api")

controllers = [CourseStatusController(), CreateUserController(), HelloWorldController(), TrackCourseController()]

for controller in controllers:
    coursegrab.add_url_rule(
        controller.get_path(), controller.get_name(), controller.response, methods=controller.get_methods()
    )
