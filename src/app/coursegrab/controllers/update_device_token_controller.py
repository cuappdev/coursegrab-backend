from . import *


class UpdateDeviceTokenController(AppDevController):
    def get_path(self):
        return "/users/device-token/"

    def get_methods(self):
        return ["POST"]

    @authorize_user
    def content(self, **kwargs):
        data = request.get_json()
        user = kwargs.get("user")
        is_ios = data.get("is_ios")
        device_token = data.get("device_token")
        user = users_dao.update_device_token(user.id, is_ios, device_token)
