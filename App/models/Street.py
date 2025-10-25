from App.database import db


class Street(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    # Relationship, a street can have many residents
    residents = db.relationship("Resident", backref="street", lazy=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"ID: {self.id} | Street {self.name}"

    def get_json(self):
        return {
            "id": self.id,
            "name": self.name,
        }
