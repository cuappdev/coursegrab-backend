import json
import pytest
from app import app, db
from app.coursegrab.dao import courses_dao, sections_dao, users_dao
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
    _, user = users_dao.create_user("test@email.com", "First", "Last")
    return user


def test_hello_world(client, user):
    res = client_get(client, user, "/api/hello/")

    assert res["success"]
    assert res["data"] == {"message": "Hello, world!"}


def test_update_session(client, user):
    req = client.post(
        "/api/session/update/",
        content_type="application/json",
        headers={"Authorization": "Bearer " + user.update_token},
    )
    res = json.loads(req.data)

    assert res["success"]
    assert res["data"] == user.serialize_session()


def test_retrieve_tracking_none(client, user):
    res = client_get(client, user, "/api/users/tracking/")

    assert res["success"]
    assert res["data"] == []


def test_track_section(client, user):
    course = ("CS", 5430, "System Security")
    section = (12350, "001", "OPEN", "Staff")
    created_section = sections_dao.create_sections(course, [section])[0]

    res = client_post(client, user, "/api/sections/track/", {"course_id": 12350})

    assert res["success"]
    assert res["data"] == {**created_section.serialize(), "is_tracking": True}

    res = client_get(client, user, "/api/users/tracking/")

    assert res["success"]
    assert res["data"] == [{**created_section.serialize(), "is_tracking": True}]


def test_untrack_section(client, user):
    course = ("CS", 6840, "Algorithmic Game Theory")
    section = (17376, "001", "CLOSED", "Staff")
    created_section = sections_dao.create_sections(course, [section])[0]

    client_post(client, user, "/api/sections/track/", {"course_id": 17376})

    res = client_post(client, user, "/api/sections/untrack/", {"course_id": 17376})

    assert res["success"]
    assert res["data"] == {**created_section.serialize(), "is_tracking": False}

    res = client_get(client, user, "/api/users/tracking/")

    assert res["success"]
    assert res["data"] == []


def test_search_course(client, user):
    course = ("CS", 5430, "System Security")
    section = (12350, "001", "OPEN", "Staff")
    sections_dao.create_sections(course, [section])[0]

    res = client_post(client, user, "/api/courses/search/", {"query": "CS"})

    assert res["success"]

    created_course = courses_dao.get_course_by_subject_and_course_num("CS", 5430)
    assert res["data"][0] == created_course.serialize_with_user(user.id)


def test_update_device_token(client, user):
    res = client_post(client, user, "/api/users/device-token/", {"device_token": "ABC123"})

    assert res["success"]

    assert user.device_token == "ABC123"


def test_update_notification(client, user):
    res = client_post(client, user, "/api/users/notification/", {"notification": "IPHONE"})

    assert res["success"]

    assert user.notification == "IPHONE"


def test_turn_off_notification(client, user):
    res = client_post(client, user, "/api/users/notification/", {"notification": "NONE"})

    assert res["success"]

    assert user.notification is None
