from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import environ

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % environ["DB_FILENAME"]
db = SQLAlchemy(app)

if __name__ == "__main__":
    app.run(host="localhost", port=environ["PORT"])
