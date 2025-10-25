from App.models import Driver, User, Street, Drive, StopRequest
from App.database import db
from datetime import datetime
from sqlalchemy.orm import joinedload, selectinload


"""
Required Command for Driver
"""


def schedule_drive(driver_id, street_name, time_str):
    # Fetch driver and street
    driver = db.session.get(Driver, driver_id)
    if not driver:
        raise ValueError("Driver not found")

    street = Street.query.filter_by(name=street_name).first()
    if not street:
        raise ValueError(f"Street '{street_name}' not found")

    try:
        scheduled_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
    except ValueError:
        raise ValueError("Invalid time format. Please use 'YYYY-MM-DD HH:MM'.")

    # Create and save the drive
    new_drive = Drive(
        driver_id=driver.id, street_id=street.id, scheduled_time=scheduled_time
    )
    db.session.add(new_drive)
    db.session.commit()
    return f"Success: Drive scheduled for {driver.username} on {street.name} at {scheduled_time}"


"""
Extra CRUD Operations for Driver
"""

# CREATE


def add_driver(
    username, password, status="Off Duty", current_location="Unknown", **kwargs
):
    if not User.query.filter_by(username=username).first():
        new_driver = Driver(
            username=username,
            password=password,
            status=status,
            current_location=current_location,
            **kwargs,
        )
        db.session.add(new_driver)
        db.session.commit()
        return new_driver
    else:
        raise ValueError(f"Driver '{username}' already exists")


# READ


def get_driver_by_id(driver_id):
    return db.session.get(Driver, driver_id)


def get_driver_details_json(driver_id):
    driver = get_driver_by_id(driver_id)
    if not driver:
        raise ValueError("Driver not found")
    return driver.get_json()


def get_all_drivers():
    drivers = Driver.query.all()
    return [str(d) for d in drivers] or ["No drivers found"]


def get_all_drivers_json():
    drivers = Driver.query.all()
    if not drivers:
        return []
    return [driver.get_json() for driver in drivers]


def get_all_drivers_summary():
    drivers = Driver.query.all()
    if not drivers:
        return ["No drivers found"]
    return [f"ID: {d.id} | Driver: {d.username}" for d in drivers]


def get_stop_requests_for_driver(driver_id):
    # Fetch driver with related drives and stop requests
    driver = Driver.query.options(
        selectinload(Driver.drives)
        .selectinload(Drive.stop_requests)
        .joinedload(StopRequest.resident)
    ).get(driver_id)

    if not driver:
        raise ValueError("Driver not found")

    requests = [
        f"Drive ID: {d.id} | Time: {d.scheduled_time.strftime('%Y-%m-%d %I:%M %p')} | Resident: {r.resident.username} | Message: {r.message}"
        for d in driver.drives
        for r in d.stop_requests
    ]

    return requests or [f"No stop requests found for driver '{driver.username}'"]


# UPDATE


def update_driver_status(driver_id, new_status, new_location):
    # Fetch driver
    driver = Driver.query.get(driver_id)
    if not driver:
        raise ValueError("Driver not found")

    driver.status = new_status
    driver.current_location = new_location
    db.session.commit()

    return f"Success: {driver.username}'s status updated to '{new_status}' at '{new_location}'."
