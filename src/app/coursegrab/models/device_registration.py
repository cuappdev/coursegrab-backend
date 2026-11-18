from datetime import datetime

from app import db


class DeviceRegistration(db.Model):
    __tablename__ = "device_registrations"
    __table_args__ = (db.UniqueConstraint("device_type", "device_token", name="uq_device_type_token"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    device_type = db.Column(db.String, nullable=False)
    device_token = db.Column(db.String, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user = db.relationship("User", back_populates="devices")

    def serialize(self):
        return {"id": self.id, "device_type": self.device_type}
