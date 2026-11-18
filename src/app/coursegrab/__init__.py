from flask import Blueprint
from app.coursegrab.controllers.current_user_controller import *
from app.coursegrab.controllers.get_course_by_id_controller import *
from app.coursegrab.controllers.get_section_controller import *
from app.coursegrab.controllers.hello_world_controller import *
from app.coursegrab.controllers.initialize_session_controller import *
from app.coursegrab.controllers.retrieve_tracking_controller import *
from app.coursegrab.controllers.search_course_controller import *
from app.coursegrab.controllers.send_android_notification_controller import *
from app.coursegrab.controllers.send_ios_notification_controller import *
from app.coursegrab.controllers.track_section_controller import *
from app.coursegrab.controllers.untrack_section_controller import *
from app.coursegrab.controllers.update_device_token_controller import *
from app.coursegrab.controllers.update_notification_controller import *
from app.coursegrab.controllers.update_session_controller import *

shared_controllers = [
    GetCourseByIDController(),
    GetSectionController(),
    HelloWorldController(),
    RetrieveTrackingController(),
    SearchCourseController(),
    TrackSectionController(),
    UntrackSectionController(),
    UpdateNotificationController(),
]

# CourseGrab Blueprint
coursegrab = Blueprint("coursegrab", __name__, url_prefix="/api")

controllers = [
    InitializeSessionController(),
    SendAndroidNotificationController(),
    SendiOSNotificationController(),
    UpdateDeviceTokenController(),
    UpdateSessionController(),
]

for controller in shared_controllers + controllers:
    coursegrab.add_url_rule(
        controller.get_path(), controller.get_name(), controller.response, methods=controller.get_methods()
    )

# CourseGrab V2 Blueprint
coursegrab_v2 = Blueprint("coursegrab_v2", __name__, url_prefix="/api/v2")

v2_controllers = [
    CurrentUserController(),
]

for controller in shared_controllers + v2_controllers:
    coursegrab_v2.add_url_rule(
        controller.get_path(), controller.get_name(), controller.response, methods=controller.get_methods()
    )
