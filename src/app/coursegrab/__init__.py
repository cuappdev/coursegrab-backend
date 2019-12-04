from flask import Blueprint
from app.coursegrab.controllers.hello_world_controller import *

# CourseGrab Blueprint
coursegrab = Blueprint("coursegrab", __name__, url_prefix="/api")

controllers = [HelloWorldController()]

for controller in controllers:
    coursegrab.add_url_rule(
        controller.get_path(), controller.get_name(), controller.response, methods=controller.get_methods()
    )
