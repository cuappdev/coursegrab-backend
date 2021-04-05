from flask_sqlalchemy import SQLAlchemy
from app import app, db
from app.coursegrab.models.session import Session
import datetime

# Deletes user sessions that have been last used 10 weeks or more ago
def delete_old_sessions():
  sessions = Session.query.all()
  outdated_sessions = []
  for s in sessions:
    if s.session_expiration < datetime.datetime.now() or s.last_used <= (datetime.datetime.now() - datetime.timedelta(weeks=10)): 
      db.session.delete(s)
      outdated_sessions.append(s.serialize_session())
  db.session.commit()
  return outdated_sessions

# Test delete old sessions conditions
def test():
  new_session = Session(device_token="test", device_type="PHONE", user_id=1)
  db.session.add(new_session)
  assert delete_old_sessions() == []
  db.session.commit()
  new_session.last_used = datetime.datetime.now() - datetime.timedelta(weeks=11)
  assert delete_old_sessions() == [new_session.serialize_session()]