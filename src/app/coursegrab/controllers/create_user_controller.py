from . import *


class CreateUserController(AppDevController):
    def get_path(self):
        return "/users/create/"

    def get_methods(self):
        return ["POST"]

    def content(self, **kwargs):
        data = request.get_json()
        email = data.get("email")
        first_name = data.get("first_name")
        last_name = data.get("last_name")

        if not (email and first_name and last_name):
            raise Exception("Missing required attributes.")

        valid, user = users_dao.create_user(email, first_name, last_name)

        if not valid:
            raise Exception("User already exists.")

        return user.serialize()
