from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ, path

base_dir = path.abspath(path.dirname(__file__)) + path.sep

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % (base_dir + environ["DB_FILENAME"])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)

from app.coursegrab import coursegrab as coursegrab  # noqa: E402

app.register_blueprint(coursegrab)
