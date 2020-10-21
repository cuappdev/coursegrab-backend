from . import *


class UpdateDeviceTokenController(AppDevController):
    def get_path(self):
        return "/users/device-token/"

    def get_methods(self):
        return ["POST"]

    @authorize_user
    def content(self, **kwargs):
        data = request.get_json()
        device_token = data.get("device_token")
        session = kwargs.get("session")
        session = sessions_dao.update_device_token(session.id, device_token)
