from flask import Blueprint
from app.coursegrab.controllers.hello_world_controller import *
from app.coursegrab.controllers.initialize_session_controller import *
from app.coursegrab.controllers.retrieve_tracking_controller import *
from app.coursegrab.controllers.track_course_controller import *
from app.coursegrab.controllers.untrack_course_controller import *
from app.coursegrab.controllers.update_session_controller import *

# CourseGrab Blueprint
coursegrab = Blueprint("coursegrab", __name__, url_prefix="/api")

controllers = [
    HelloWorldController(),
    InitializeSessionController(),
    RetrieveTrackingController(),
    TrackCourseController(),
    UntrackCourseController(),
    UpdateSessionController(),
]

for controller in controllers:
    coursegrab.add_url_rule(
        controller.get_path(), controller.get_name(), controller.response, methods=controller.get_methods()
    )
