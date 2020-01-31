from app import app, db
from os import environ

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=environ["PORT"])
