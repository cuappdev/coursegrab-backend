from flask_sqlalchemy import SQLAlchemy
from app import app, db
from app.coursegrab.models.session import Session
import datetime

# Deletes user sessions that have been last used 10 weeks or more ago
def delete_old_sessions():
  sessions = Session.query.all()
  outdated_sessions = []
  for s in sessions:
    if s.session_expiration <= datetime.datetime.now() or s.last_used <= (datetime.datetime.now() - datetime.timedelta(weeks=10)): 
      db.session.delete(s)
      outdated_sessions.append(s.serialize_session())
  db.session.commit()
  return outdated_sessions

# Test delete old sessions function
def test():
  new_session = Session(device_token="test", device_type="PHONE", user_id=1)
  db.session.add(new_session)
  assert delete_old_sessions() == []

  new_session.last_used = datetime.datetime.now() - datetime.timedelta(weeks=11)
  assert delete_old_sessions() == [new_session.serialize_session()]

  expired_session = Session(device_token="test3", device_type="PHONE", user_id=1)
  expired_session.session_expiration = datetime.datetime.now() - datetime.timedelta(weeks=1)
  db.session.add(expired_session)
  assert delete_old_sessions() == [expired_session.serialize_session()]

  new_expired_session = Session(device_token="test4", device_type="PHONE", user_id=1)
  new_expired_session.session_expiration = datetime.datetime.now()
  db.session.add(new_expired_session)
  assert delete_old_sessions() == [new_expired_session.serialize_session()]

  last_session = Session(device_token="test5", device_type="PHONE", user_id=1)
  db.session.add(last_session)
  last_session.last_used = datetime.datetime.now() - datetime.timedelta(weeks=10)
  assert delete_old_sessions() == [last_session.serialize_session()]

