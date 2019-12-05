from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import environ

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % environ["DB_FILENAME"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)

from app.coursegrab import coursegrab as coursegrab  # noqa: E402

app.register_blueprint(coursegrab)
