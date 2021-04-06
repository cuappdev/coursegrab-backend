from flask_sqlalchemy import SQLAlchemy
from app import app, db
from app.coursegrab.models.session import Session
import datetime

def delete_old_sessions():
  """ Deletes user sessions that have been last used 10 weeks or more ago. """
  sessions = Session.query.filter(Session.last_used <= datetime.datetime.now() - datetime.timedelta(weeks=10))
  outdated_sessions = []
  for s in sessions:
      db.session.delete(s)
      outdated_sessions.append(s.serialize())
  db.session.commit()
  return outdated_sessions
