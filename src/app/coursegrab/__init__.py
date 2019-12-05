from flask import Blueprint
from app.coursegrab.controllers.create_user_controller import *
from app.coursegrab.controllers.hello_world_controller import *
from app.coursegrab.controllers.login_controller import *
from app.coursegrab.controllers.oauth2_callback_controller import *
from app.coursegrab.controllers.track_course_controller import *
from app.coursegrab.controllers.update_session_controller import *

# CourseGrab Blueprint
coursegrab = Blueprint("coursegrab", __name__, url_prefix="/api")

controllers = [
    CreateUserController(),
    HelloWorldController(),
    LoginController(),
    OAuth2CallbackController(),
    TrackCourseController(),
    UpdateSessionController(),
]

for controller in controllers:
    coursegrab.add_url_rule(
        controller.get_path(), controller.get_name(), controller.response, methods=controller.get_methods()
    )