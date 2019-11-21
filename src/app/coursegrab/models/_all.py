from marshmallow_sqlalchemy import ModelSchema
from app.coursegrab.models.user import *
from app.coursegrab.models.course import *


class UserSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = User


class CourseSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Course
