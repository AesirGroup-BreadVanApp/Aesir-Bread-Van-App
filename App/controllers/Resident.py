from App.models import StopRequest, User, Resident, Drive, Driver, Street
from App.database import db
from sqlalchemy.orm import joinedload

"""
Required Commands for Resident
"""


def get_resident_inbox(resident_id):
    # Fetch resident and their street's drives (inbox)
    resident = Resident.query.get(resident_id)
    if not resident:
        raise ValueError("Resident not found")

    drives = (
        Drive.query.options(joinedload(Drive.driver))
        .filter_by(street_id=resident.street_id)
        .order_by(Drive.scheduled_time.asc())
        .all()
    )

    if not drives:
        return [f"No upcoming drives scheduled for street '{resident.street.name}'"]
    else:
        inbox = [
            f"Drive ID: {d.id} | Driver: {d.driver.username} | Scheduled Time: {d.scheduled_time.strftime('%Y-%m-%d %H:%M')}"
            for d in drives
        ]
        return inbox


def request_stop(resident_id, drive_id, message):
    # Fetch resident and drive
    resident = Resident.query.get(resident_id)
    if not resident:
        raise ValueError("Resident not found")

    drive = Drive.query.options(joinedload(Drive.driver)).get(drive_id)
    if not drive:
        raise ValueError("Drive not found")

    if drive.street_id != resident.street_id:
        raise ValueError("Error: You can only request stops for drives on your street")

    new_request = StopRequest(
        resident_id=resident.id, drive_id=drive.id, message=message
    )
    db.session.add(new_request)
    db.session.commit()
    return f"Success: Stop request sent to driver {drive.driver.username} for drive on {drive.scheduled_time.strftime('%Y-%m-%d %H:%M')}"


def get_driver_status_and_location(driver_id):
    # Fetch driver
    driver = db.session.get(Driver, driver_id)
    if not driver:
        raise ValueError("Driver not found")
    return f"Driver: {driver.username} | Status: {driver.status} | Current Location: {driver.current_location}"


"""
Extra CRUD Operations for Resident
"""

# CREATE


def add_resident(username, password, street_name):
    # Check if resident with the same username already exists
    if not User.query.filter_by(username=username).first():
        # Check if street exists
        street = Street.query.filter_by(name=street_name).first()
        if not street:
            raise ValueError(f"Street '{street_name}' not found")

        new_resident = Resident(
            username=username, password=password, street_id=street.id
        )
        db.session.add(new_resident)
        db.session.commit()
        return new_resident
    else:
        raise ValueError(f"Resident '{username}' already exists")


# READ


def get_resident_by_id(resident_id):
    return db.session.get(Resident, resident_id)


def get_all_residents():
    residents = Resident.query.options(joinedload(Resident.street)).all()
    return [str(r) for r in residents] or ["No residents found"]


def get_all_residents_json():
    residents = Resident.query.options(joinedload(Resident.street)).all()
    if not residents:
        return []
    return [resident.get_json() for resident in residents]


def get_all_residents_summary():
    residents = Resident.query.options(joinedload(Resident.street)).all()
    if not residents:
        return ["No residents found"]
    return [
        f"ID: {r.id} | Resident: {r.username} | Street: {r.street.name}"
        for r in residents
    ]


# UPDATE


def update_resident_street(resident_id, new_street_name):
    # Fetch resident
    resident = db.session.get(Resident, resident_id)
    if not resident:
        raise ValueError("Resident not found")

    # Fetch new street
    new_street = Street.query.filter_by(name=new_street_name).first()
    if not new_street:
        raise ValueError(f"Street '{new_street_name}' not found")

    # Update resident's street
    resident.street_id = new_street.id
    db.session.add(resident)
    db.session.commit()
    return resident
