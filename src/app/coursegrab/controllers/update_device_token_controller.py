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
        device_token = data.get("device_token")
        user = users_dao.update_device_token(user.id, device_token)
