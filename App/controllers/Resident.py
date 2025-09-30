from App.models import StopRequest, User, Resident, Drive, Driver, Street
from App.database import db
from sqlalchemy.orm import joinedload

"""
Required Commands for Resident
"""


def get_resident_inbox(resident_id):
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
    driver = db.session.get(Driver, driver_id)
    if not driver:
        raise ValueError("Driver not found")
    return f"Driver: {driver.username} | Status: {driver.status} | Current Location: {driver.current_location}"


"""
Commands I decided to add for Resident
"""


def add_resident(username, password, street_name):
    if not User.query.filter_by(username=username).first():
        street = Street.query.filter_by(name=street_name).first()
        if not street:
            raise ValueError(f"Street '{street_name}' not found")

        new_resident = Resident(
            username=username, password=password, street_id=street.id
        )
        db.session.add(new_resident)
        db.session.commit()
        return new_resident


def get_all_residents():
    residents = Resident.query.options(joinedload(Resident.street)).all()
    return [str(r) for r in residents] or ["No residents found"]


def get_all_residents_summary():
    residents = Resident.query.options(joinedload(Resident.street)).all()
    if not residents:
        return ["No residents found"]
    return [
        f"ID: {r.id} | Resident: {r.username} | Street: {r.street.name}"
        for r in residents
    ]
