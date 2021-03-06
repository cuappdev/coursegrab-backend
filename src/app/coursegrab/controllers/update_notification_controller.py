from . import *
from app.coursegrab.utils.constants import NONE


class UpdateNotificationController(AppDevController):
    def get_path(self):
        return "/users/notification/"

    def get_methods(self):
        return ["POST"]

    @authorize_user
    def content(self, **kwargs):
        data = request.get_json()
        user = kwargs.get("user")

        # NONE is a constant imported from constants.py with string value "None"
        # Following line of code converts the NONE="None" string value into Python's null value None
        notification = None if data.get("notification") == NONE else data.get("notification")
        user = users_dao.update_notification(user.id, notification)
