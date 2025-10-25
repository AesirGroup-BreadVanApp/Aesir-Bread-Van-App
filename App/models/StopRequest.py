from App.database import db


class StopRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(200), nullable=True)

    # Foreign keys
    resident_id = db.Column(db.Integer, db.ForeignKey("resident.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("drive.id"), nullable=False)

    def __init__(self, resident_id, drive_id, message=None):
        self.resident_id = resident_id
        self.drive_id = drive_id
        self.message = message

    def __repr__(self):
        return f"StopRequest ID: {self.id} | Resident ID: {self.resident_id} | Drive ID: {self.drive_id} | Message: {self.message}"

    def get_json(self):
        return {
            "id": self.id,
            "resident_id": self.resident_id,
            "drive_id": self.drive_id,
            "message": self.message,
        }
