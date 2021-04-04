from flask_sqlalchemy import SQLAlchemy
from app import app, db
from app.coursegrab.models.session import Session
import datetime

def delete_old_sessions():
  sessions = [s.serialize_session() for s in Session.query.all()]
  outdated_sessions = []
  for s in sessions:
    if s["session_expiration"] < datetime.datetime.now() or s["last_used"] > (datetime.datetime.now() - datetime.timedelta(weeks=10)): 
      db.session.delete(s)
      outdated_sessions.append(s)
  db.session.commit()
  return outdated_sessions

def test():
  new_session = db.Session(device_token="test", device_type="PHONE", user_id=1)
  db.session.add(new_session)
  db.session.commit()
  assert delete_old_sessions() == []
  new_session["last_used"] = datetime.datetime.now() - datetime.timedelta(weeks=11)
  assert delete_old_sessions() == [new_session.serialize_session()]

# delete_old_sessions()