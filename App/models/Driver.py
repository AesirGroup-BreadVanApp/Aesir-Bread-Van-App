from App.database import db
from App.models.user import User


class Driver(User):
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    status = db.Column(db.String(20), default="Off Duty", nullable=False)
    current_location = db.Column(db.String(120), default="Unknown")

    # Relationship, the driver can have many drives
    drives = db.relationship("Drive", backref="driver", lazy=True)

    __mapper_args__ = {
        "polymorphic_identity": "driver",
    }

    def __init__(self, username, password, status, current_location, **kwargs):
        super().__init__(username=username, password=password, **kwargs)
        self.status = status
        self.current_location = current_location

    def __repr__(self):
        return f"ID: {self.id} | Driver: {self.username} | Status: {self.status} | Location: {self.current_location}"

    def get_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "status": self.status,
            "current_location": self.current_location,
        }
