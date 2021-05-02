from flask import Blueprint
from app.coursegrab.controllers.get_section_controller import *
from app.coursegrab.controllers.hello_world_controller import *
from app.coursegrab.controllers.initialize_session_controller import *
from app.coursegrab.controllers.initialize_session_v2_controller import *
from app.coursegrab.controllers.retrieve_tracking_controller import *
from app.coursegrab.controllers.search_course_controller import *
from app.coursegrab.controllers.send_android_notification_controller import *
from app.coursegrab.controllers.send_ios_notification_controller import *
from app.coursegrab.controllers.track_section_controller import *
from app.coursegrab.controllers.untrack_section_controller import *
from app.coursegrab.controllers.update_device_token_controller import *
from app.coursegrab.controllers.update_notification_controller import *
from app.coursegrab.controllers.update_session_controller import *
from app.coursegrab.controllers.update_session_v2_controller import *

# CourseGrab Blueprint
coursegrab = Blueprint("coursegrab", __name__, url_prefix="/api")

controllers = [
    GetSectionController(),
    HelloWorldController(),
    InitializeSessionController(),
    InitializeSessionV2Controller(),
    RetrieveTrackingController(),
    SearchCourseController(),
    SendAndroidNotificationController(),
    SendiOSNotificationController(),
    TrackSectionController(),
    UntrackSectionController(),
    UpdateDeviceTokenController(),
    UpdateNotificationController(),
    UpdateSessionController(),
    UpdateSessionV2Controller(),
]

for controller in controllers:
    coursegrab.add_url_rule(
        controller.get_path(), controller.get_name(), controller.response, methods=controller.get_methods()
    )
