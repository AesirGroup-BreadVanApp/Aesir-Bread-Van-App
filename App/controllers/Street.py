from App.models import Street
from App.database import db


# CREATE
def add_street(name):
    # Check if street already exists
    if not Street.query.filter_by(name=name).first():
        new_street = Street(name=name)
        db.session.add(new_street)
        db.session.commit()
        return new_street
    else:
        raise ValueError(f"Street '{name}' already exists")


# READ
def get_street_by_id(street_id):
    return db.session.get(Street, street_id)


def get_street_by_name(name):
    return Street.query.filter_by(name=name).first()


def get_all_streets():
    streets = Street.query.all()
    return [str(s) for s in streets] or ["No streets found"]


def get_all_streets_json():
    streets = Street.query.all()
    if not streets:
        return []
    return [street.get_json() for street in streets]


# UPDATE
def update_street_name(street_id, street_name):
    street = get_street_by_id(street_id)
    if street:
        street.name = street_name
        db.session.commit()
        return True
    return None


# DELETE
def delete_street(street_id):
    street = get_street_by_id(street_id)
    if street:
        db.session.delete(street)
        db.session.commit()
        return True
    return None
