from app import app, db
from app.coursegrab.utils.scraper import start_update
from os import environ

with app.app_context():
    db.create_all()

start_update()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=environ["PORT"], debug=False)
