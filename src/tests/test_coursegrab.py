import json
import pytest
from app import app, db
from app.coursegrab.dao import courses_dao, sections_dao, Session, sessions_dao, User, users_dao
from app.coursegrab.utils.constants import IOS
from .helpers import client_get, client_post


@pytest.fixture
def client():
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

    db.drop_all()


@pytest.fixture
def user():
    return users_dao.create_user("test@email.com", "First", "Last")


@pytest.fixture
def session(user):
    return sessions_dao.create_session(user.id, IOS)


def test_hello_world(client, session):
    res = client_get(client, session, "/api/hello/")

    assert res["success"]
    assert res["data"] == {"message": "Hello, world!"}


def test_update_session(client, session):
    req = client.post(
        "/api/session/update/",
        content_type="application/json",
        headers={"Authorization": "Bearer " + session.update_token},
    )
    res = json.loads(req.data)

    assert res["success"]
    assert res["data"] == session.serialize_session()


def test_cascade_delete_session(client, user, session):
    assert User.query.count() == 1
    assert Session.query.count() == 1

    db.session.delete(user)
    db.session.commit()

    assert User.query.count() == 0
    assert Session.query.count() == 0


def test_retrieve_tracking_none(client, session):
    res = client_get(client, session, "/api/users/tracking/")

    assert res["success"]
    assert res["data"]["sections"] == []


def test_track_section(client, session):
    course = ("CS", 5430, "System Security")
    section = (12350, "001", "OPEN", "Staff", "Online")
    created_section = sections_dao.create_sections(course, [section])[0]

    res = client_post(client, session, "/api/sections/track/", {"course_id": 12350})

    assert res["success"]
    assert res["data"] == {**created_section.serialize(), "is_tracking": True}

    res = client_get(client, session, "/api/users/tracking/")

    assert res["success"]
    assert res["data"]["sections"] == [{**created_section.serialize(), "is_tracking": True}]


def test_untrack_section(client, session):
    course = ("CS", 6840, "Algorithmic Game Theory")
    section = (17376, "001", "CLOSED", "Staff", "Online")
    created_section = sections_dao.create_sections(course, [section])[0]

    client_post(client, session, "/api/sections/track/", {"course_id": 17376})

    res = client_post(client, session, "/api/sections/untrack/", {"course_id": 17376})

    assert res["success"]
    assert res["data"] == {**created_section.serialize(), "is_tracking": False}

    res = client_get(client, session, "/api/users/tracking/")

    assert res["success"]
    assert res["data"]["sections"] == []


def test_search_course(client, session, user):
    course = ("CS", 5430, "System Security")
    section = (12350, "001", "OPEN", "Staff", "Online")
    sections_dao.create_sections(course, [section])[0]

    query = "CS"
    res = client_post(client, session, "/api/courses/search/", {"query": query})

    assert res["success"]

    created_course = courses_dao.get_course_by_subject_and_course_num("CS", 5430)
    assert res["data"]["courses"][0] == created_course.serialize_with_user(user.id)
    assert res["data"]["query"] == query


def test_update_device_token(client, session, user):
    res = client_post(client, session, "/api/users/device-token/", {"device_token": "ABC123"})
    session_from_user = [s.serialize() for s in user.sessions]

    assert res["success"]

    assert session.device_token == "ABC123"
    assert session_from_user[0]["device_token"] == "ABC123"


def test_update_notification(client, session, user):
    res = client_post(client, session, "/api/users/notification/", {"notification": "IOS"})

    assert res["success"]

    assert user.notification == "IOS"


def test_turn_off_notification(client, session, user):
    res = client_post(client, session, "/api/users/notification/", {"notification": "NONE"})

    assert res["success"]

    assert user.notification is None


def test_create_session_existing_device_token(client, session, user):
    device_token = "ABC123"
    res = client_post(client, session, "/api/users/device-token/", {"device_token": device_token})

    assert res["success"]

    new_session = sessions_dao.create_session(user.id, session.device_type, device_token)

    assert new_session.id == session.id
    assert new_session.session_token == session.session_token
    assert new_session.device_token == device_token


def test_create_session_no_device_token(client, session, user):
    sessions_dao.create_session(user.id, session.device_type)

    assert len(user.sessions) == 2


def test_delete_session_expired_device_token(client, session, user):
    new_session = sessions_dao.create_session(user.id, session.device_type)

    assert Session.query.count() == 2

    sessions_dao.delete_session_expired_device_tokens([session.device_token, new_session.device_token])

    assert Session.query.count() == 0
