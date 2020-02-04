import json
import pytest
from app import app, db
from app.coursegrab.dao import sections_dao, users_dao
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
    assert "session_token" in res["data"]
    assert "session_expiration" in res["data"]
    assert "update_token" in res["data"]


def test_retrieve_tracking_none(client, user):
    res = client_get(client, user, "/api/users/tracking/")

    assert res["success"]
    assert res["data"] == []


def test_track_section(client, user):
    course = ("CS", 5430, "System Security")
    section = (12350, "001", "OPEN")
    created_section = sections_dao.create_sections(course, [section])[0]

    res = client_post(client, user, "/api/sections/track/", {"course_id": 12350})

    assert res["success"]
    assert res["data"] == {**created_section.serialize(), "is_tracking": True}

    res = client_get(client, user, "/api/users/tracking/")

    assert res["success"]
    assert res["data"] == [{**created_section.serialize(), "is_tracking": True}]


def test_untrack_section(client, user):
    course = ("CS", 6840, "Algorithmic Game Theory")
    section = (17376, "001", "OPEN")
    created_section = sections_dao.create_sections(course, [section])[0]

    client_post(client, user, "/api/sections/track/", {"course_id": 17376})

    res = client_post(client, user, "/api/sections/untrack/", {"course_id": 17376})

    assert res["success"]
    assert res["data"] == {**created_section.serialize(), "is_tracking": False}

    res = client_get(client, user, "/api/users/tracking/")

    assert res["success"]
    assert res["data"] == []
