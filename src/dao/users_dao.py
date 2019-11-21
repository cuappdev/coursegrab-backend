from app import db
from models.user import User


def get_user_by_id(id):
    return User.query.get(id)


def get_user_by_email(email):
    return User.query.filter(User.email == email).first()


def create_user(email, first_name, last_name):
    optional_user = get_user_by_email(email)

    if optional_user:
        return False, optional_user

    user = User(email=email, first_name=first_name, last_name=last_name)
    db.session.add(user)
    db.session.commit()
    return True, user
