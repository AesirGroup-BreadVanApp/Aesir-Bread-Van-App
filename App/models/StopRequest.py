from App.database import db

class StopRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(200), nullable=True)

    # Foreign keys
    resident_id = db.Column(db.Integer, db.ForeignKey('resident.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'), nullable=False)