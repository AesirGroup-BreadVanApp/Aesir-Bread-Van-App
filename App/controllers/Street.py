from App.models import Street
from App.database import db

def add_street(name):
    if not Street.query.filter_by(name=name).first():
        new_street = Street(name=name)
        db.session.add(new_street)
        db.session.commit()
        return new_street