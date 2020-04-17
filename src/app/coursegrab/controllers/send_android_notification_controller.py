from . import *
from ..models.section import Section
from ..utils.push_notifications import create_payload, send_android_notification


class SendAndroidNotificationController(AppDevController):
    def get_path(self):
        return "/notification/android/<device_token>/"

    def get_methods(self):
        return ["GET"]

    def content(self, **kwargs):
        device_token = request.view_args["device_token"]
        section = Section.query.first()
        if send_android_notification([device_token], create_payload(section)) == 1:
            return {"message": "Notification was successfully sent."}
        else:
            return {"message": "Notification was unsuccessfully sent."}
