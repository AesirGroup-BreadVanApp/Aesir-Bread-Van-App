from App.database import db
from App.models import User


class Resident(User):
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)

    # Foreign Key
    street_id = db.Column(db.Integer, db.ForeignKey("street.id"), nullable=False)

    # Relationship, the resident can make many stop requests
    stop_requests = db.relationship("StopRequest", backref="resident", lazy=True)

    __mapper_args__ = {
        "polymorphic_identity": "resident",
    }

    def __init__(self, username, password, street_id, **kwargs):
        super().__init__(username=username, password=password, **kwargs)
        if street_id is None or street_id < 0:
            raise ValueError("street_id cannot be None or negative")
        else:
            self.street_id = street_id

    def __repr__(self):
        return f"ID: {self.id} | Username: {self.username} | Street: {self.street.name}"

    def get_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "street_id": self.street_id,
            "street_name": self.street.name,
        }
