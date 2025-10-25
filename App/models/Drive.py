from App.database import db
from datetime import datetime


class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scheduled_time = db.Column(db.DateTime, nullable=False)

    # Foreign keys
    driver_id = db.Column(db.Integer, db.ForeignKey("driver.id"), nullable=False)
    street_id = db.Column(db.Integer, db.ForeignKey("street.id"), nullable=False)

    # Relationship, a drive can have many stop requests
    stop_requests = db.relationship("StopRequest", backref="drive", lazy=True)

    def __init__(self, driver_id, street_id, scheduled_time):
        self.driver_id = driver_id
        self.street_id = street_id
        self.scheduled_time = scheduled_time

    def __repr__(self):
        return f"Drive ID: {self.id} | Street: {self.street.name} | Driver: {self.driver.username} | Time: {self.scheduled_time.strftime('%Y-%m-%d %I:%M %p')}"

    def get_json(self):
        return {
            "id": self.id,
            "driver_id": self.driver_id,
            "street_id": self.street_id,
            "scheduled_time": self.scheduled_time,
        }
