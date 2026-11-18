from unittest.mock import Mock

import pytest
from firebase_admin import auth, exceptions

from app import app, db
from app.coursegrab.dao import sections_dao, sessions_dao, users_dao
from app.coursegrab.models.user import User
from app.coursegrab.utils import firebase


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setitem(app.config, "SQLALCHEMY_DATABASE_URI", "sqlite:///" + str(tmp_path / "auth.db"))
    monkeypatch.setitem(app.config, "TESTING", True)
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def claims():
    return {
        "uid": "firebase-user", "email": "student@cornell.edu", "email_verified": True,
        "name": "First Last", "firebase": {"sign_in_provider": "google.com"},
    }


@pytest.fixture
def verifier(monkeypatch, claims):
    monkeypatch.setattr(firebase, "get_firebase_app", lambda: "test-app")
    monkeypatch.setattr(firebase.auth, "get_user", Mock(return_value=Mock(disabled=False)))
    verify = Mock(return_value=claims)
    monkeypatch.setattr(firebase.auth, "verify_id_token", verify)
    return verify


def headers(token="firebase-token"):
    return {"Authorization": "Bearer " + token}


def test_initialize_links_existing_user_and_preserves_data(client, verifier):
    user = users_dao.create_user("student@cornell.edu", "Original", "Name")
    users_dao.update_notification(user.id, "IOS")
    section = sections_dao.create_sections(("CS", 3110, "Programming"), [(123, "001", "OPEN", "Staff", "Online")])[0]
    users_dao.track_section(user.id, section.catalog_num)
    response = client.get("/api/v2/users/me/", headers=headers())
    assert response.status_code == 200
    assert response.json["data"]["user"]["id"] == user.id
    assert user.firebase_uid == "firebase-user"
    assert user.notification == "IOS"
    assert user.sections == [section]
    assert user.sessions == []
    assert "session_token" not in response.json["data"]
    verifier.assert_called_once_with("firebase-token", app="test-app", check_revoked=True)
    assert client.get("/api/v2/users/me/", headers=headers()).status_code == 200
    assert User.query.count() == 1


def test_new_user_and_tracking(client, verifier):
    response = client.get("/api/v2/users/tracking/", headers=headers())
    assert response.status_code == 200
    assert response.json["data"] == {"sections": []}
    assert User.query.one().firebase_uid == "firebase-user"


@pytest.mark.parametrize("header", [None, "", "Basic abc", "Bearer", "Bearer a b", "raw-token"])
def test_malformed_header(client, verifier, header):
    response = client.get("/api/v2/hello/", headers={} if header is None else {"Authorization": header})
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    verifier.assert_not_called()


@pytest.mark.parametrize("error", [
    auth.InvalidIdTokenError("wrong signature or project"),
    auth.ExpiredIdTokenError("expired", None),
    auth.RevokedIdTokenError("revoked"),
    auth.UserNotFoundError("deleted"),
])
def test_invalid_firebase_token(client, verifier, error):
    verifier.side_effect = error
    response = client.get("/api/v2/hello/", headers=headers())
    assert response.status_code == 401
    assert User.query.count() == 0


def test_service_unavailable(client, verifier):
    verifier.side_effect = exceptions.UnavailableError("outage")
    assert client.get("/api/v2/hello/", headers=headers()).status_code == 503


@pytest.mark.parametrize("changes", [
    {"email_verified": False}, {"email": None}, {"email": "student@example.com"},
    {"email": "student@cornell.edu.evil.com"}, {"email": "@cornell.edu"},
    {"firebase": {"sign_in_provider": "password"}},
])
def test_ineligible_identity(client, verifier, claims, changes):
    claims.update(changes)
    assert client.get("/api/v2/hello/", headers=headers()).status_code == 403
    assert User.query.count() == 0


@pytest.mark.parametrize("email", ["appstoreappdev@gmail.com", "coursegrab.droid@gmail.com"])
def test_review_accounts(client, verifier, claims, email):
    claims["email"] = email
    assert client.get("/api/v2/hello/", headers=headers()).status_code == 200


def test_conflicting_uid_cannot_take_existing_account(client, verifier, claims):
    client.get("/api/v2/hello/", headers=headers())
    claims["uid"] = "different-uid"
    assert client.get("/api/v2/hello/", headers=headers()).status_code == 409
    assert User.query.one().firebase_uid == "firebase-user"


def test_same_uid_email_change_preserves_user(client, verifier, claims):
    client.get("/api/v2/hello/", headers=headers())
    user_id = User.query.one().id
    claims["email"] = "changed@cornell.edu"
    assert client.get("/api/v2/hello/", headers=headers()).status_code == 200
    assert User.query.one().id == user_id
    assert User.query.one().email == "changed@cornell.edu"


def test_email_change_collision(client, verifier, claims):
    client.get("/api/v2/hello/", headers=headers())
    users_dao.create_user("taken@cornell.edu", "Other", "Person")
    claims["email"] = "taken@cornell.edu"
    assert client.get("/api/v2/hello/", headers=headers()).status_code == 409
    assert User.query.filter_by(firebase_uid="firebase-user").one().email == "student@cornell.edu"


def test_optional_auth(client, verifier):
    assert client.post("/api/v2/courses/search/", json={"query": "CS"}).status_code == 200
    verifier.assert_not_called()
    verifier.side_effect = auth.InvalidIdTokenError("invalid")
    assert client.post("/api/v2/courses/search/", json={"query": "CS"}, headers=headers()).status_code == 401


def test_legacy_tokens_rejected_on_v2(client, verifier):
    user = users_dao.create_user("student@cornell.edu", "First", "Last")
    session = sessions_dao.create_session(user.id, "IOS")
    verifier.side_effect = auth.InvalidIdTokenError("not a JWT")
    assert client.get("/api/v2/hello/", headers=headers(session.session_token)).status_code == 401
    assert client.post("/api/v2/session/update/", headers=headers(session.update_token)).status_code == 404


@pytest.mark.parametrize("same_uid", [True, False])
def test_concurrent_account_linking(client, claims, monkeypatch, same_uid):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from sqlalchemy.orm import Query
    from app.coursegrab.utils.api_error import APIError

    user = users_dao.create_user("student@cornell.edu", "First", "Last")
    user_id = user.id
    barrier = Barrier(2)
    original_all = Query.all

    def synchronized_all(query):
        result = original_all(query)
        if query.column_descriptions[0]["entity"] is User:
            barrier.wait(timeout=10)
        return result

    monkeypatch.setattr(Query, "all", synchronized_all)

    def sign_in(uid):
        with app.app_context():
            try:
                return users_dao.get_or_create_firebase_user(dict(claims, uid=uid)).id
            except APIError as error:
                return error.status_code
            finally:
                db.session.remove()

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(sign_in, ["first", "first" if same_uid else "second"]))
    db.session.expire_all()
    assert results == [user_id, user_id] if same_uid else sorted(results) == [user_id, 409]
    assert User.query.get(user_id).firebase_uid in ("first", "second")


def test_unexpected_failure_is_not_returned_as_success(client, verifier):
    verifier.side_effect = RuntimeError("private implementation details")
    response = client.get("/api/v2/hello/", headers=headers())
    assert response.status_code == 500
    assert "private implementation" not in response.get_data(as_text=True)


def test_disabled_user(client, verifier, monkeypatch):
    monkeypatch.setattr(firebase.auth, "get_user", Mock(return_value=Mock(disabled=True)))
    assert client.get("/api/v2/hello/", headers=headers()).status_code == 401
    assert User.query.count() == 0


def test_v1_and_v2_work_together_with_same_local_user(client, verifier, monkeypatch):
    from app.coursegrab.controllers.initialize_session_controller import id_token
    monkeypatch.setenv("IOS_CLIENT_ID", "test-client")
    monkeypatch.setattr(id_token, "verify_oauth2_token", Mock(return_value={
        "iss": "accounts.google.com", "email": "student@cornell.edu",
        "given_name": "First", "family_name": "Last",
    }))
    response = client.post("/api/session/initialize/", json={"token": "google-token", "device_type": "IOS"})
    assert response.status_code == 200
    legacy = response.json["data"]
    assert "session_token" in legacy
    verifier.assert_not_called()
    user_id = User.query.one().id
    section = sections_dao.create_sections(("CS", 3110, "Programming"), [(123, "001", "OPEN", "Staff", "Online")])[0]
    assert client.post("/api/sections/track/", headers=headers(legacy["session_token"]),
                       json={"course_id": section.catalog_num}).json["success"]
    assert client.get("/api/v2/users/me/", headers=headers()).json["data"]["user"]["id"] == user_id
    assert client.get("/api/v2/users/tracking/", headers=headers()).json["data"]["sections"][0]["catalog_num"] == 123
    assert client.post("/api/v2/sections/untrack/", headers=headers(), json={"course_id": 123}).json["success"]
    assert client.get("/api/users/tracking/", headers=headers(legacy["session_token"])).json["data"]["sections"] == []
    refreshed = client.post("/api/session/update/", headers=headers(legacy["update_token"]))
    assert refreshed.json["success"]
    assert "update_token" in refreshed.json["data"]
    assert client.get("/api/hello/", headers={"Authorization": refreshed.json["data"]["session_token"]}).json["success"]
    assert User.query.count() == 1


def test_firebase_token_not_accepted_on_v1(client, verifier):
    assert client.get("/api/hello/", headers=headers()).status_code == 401
    verifier.assert_not_called()


@pytest.mark.parametrize("path", ["session/initialize/", "session/update/", "users/device-token/"])
def test_v2_has_no_legacy_session_routes(client, verifier, path):
    assert client.post("/api/v2/" + path, headers=headers()).status_code == 404
    verifier.assert_not_called()
