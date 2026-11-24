from flask import request

from app.coursegrab.dao import devices_dao
from app.coursegrab.utils.appdev_controller import AppDevController
from app.coursegrab.utils.authorize import authorize_user


class RegisterDeviceController(AppDevController):
    def get_path(self):
        return "/users/devices/"

    def get_methods(self):
        return ["POST"]

    @authorize_user
    def content(self, **kwargs):
        registration = devices_dao.register_new_device(kwargs["user"].id, request.get_json(silent=True))
        return registration.serialize()


class ManageDeviceController(AppDevController):
    def get_path(self):
        return "/users/devices/<int:registration_id>/"

    def get_methods(self):
        return ["PUT", "DELETE"]

    @authorize_user
    def content(self, **kwargs):
        registration_id = request.view_args["registration_id"]
        user_id = kwargs["user"].id
        if request.method == "DELETE":
            devices_dao.unregister_device(user_id, registration_id)
            return None
        registration = devices_dao.update_device_registration(
            user_id, registration_id, request.get_json(silent=True)
        )
        return registration.serialize()
