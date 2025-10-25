import pytest
from App.main import create_app
from App.database import db, create_db
from App.models import User, Driver, Resident, Street, Drive
from App.controllers import (
    create_user,
    delete_user,
    get_user_by_username,
    get_resident_by_id,
    update_user,
    add_driver,
    add_resident,
    add_street,
    login,
    schedule_drive,
    get_resident_inbox,
    update_resident_street,
    request_stop,
    get_stop_requests_for_driver,
    update_driver_status,
)


# =============================================================================
#                               Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def empty_db():
    """
    Provides a clean in-memory database for each test.
    Automatically applies to all tests.
    """
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        create_db()
        yield
        db.session.remove()
        db.drop_all()


# =============================================================================
#                           Integration Tests
# =============================================================================


def test_user_creation_and_login():
    # Create and login a driver
    driver = add_driver("Bob", "bobpass")
    assert driver is not None
    token = login("Bob", "bobpass")
    assert token is not None
    assert login("Bob", "wrongpass") is None

    # Create and login a resident
    add_street("Main Street")
    resident = add_resident("Charlie", "charliepass", "Main Street")
    assert resident is not None
    token = login("Charlie", "charliepass")
    assert token is not None
    assert login("Charlie", "wrongpass") is None


def test_create_user_controller_and_update():
    u = create_user("initial_user", "password")
    assert u is not None
    assert get_user_by_username("initial_user") is not None

    updated = update_user(u.id, "updated_user")
    assert updated is True
    assert get_user_by_username("updated_user") is not None


def test_delete_user():
    u = create_user("to_delete", "password")
    assert u is not None
    user_id = u.id

    deleted = delete_user(user_id)
    assert deleted is True

    deleted_user = get_user_by_username("to_delete")
    assert deleted_user is None


def test_full_drive_schedule_and_inbox_flow():
    add_street("Maple Street")
    driver = add_driver("Bob", "bobpass")
    resident = add_resident("Charlie", "charliepass", "Maple Street")
    drive_time_str = "2025-12-25 15:30"

    result = schedule_drive(driver.id, "Maple Street", drive_time_str)
    assert "Success" in result

    inbox = get_resident_inbox(resident.id)
    assert len(inbox) == 1
    assert "Bob" in inbox[0]


def test_full_stop_request_flow():
    street = add_street("Oak Avenue")
    driver = add_driver("John", "johnpass")
    resident = add_resident("Diana", "dianapass", "Oak Avenue")
    drive_time_str = "2025-11-15 09:00"

    schedule_drive(driver.id, "Oak Avenue", drive_time_str)
    drive = Drive.query.filter_by(street_id=street.id).first()
    assert drive is not None

    stop_message = "Please stop at the bakery."
    request_result = request_stop(resident.id, drive.id, stop_message)
    assert "Success" in request_result

    requests = get_stop_requests_for_driver(driver.id)
    assert len(requests) == 1
    assert stop_message in requests[0]


def test_update_driver_status_success():
    d = add_driver(
        "status_driver", "password", status="On Duty", current_location="Depot"
    )
    message = update_driver_status(d.id, "Off Duty", "Coffee Shop")
    assert "Success" in message

    updated = Driver.query.get(d.id)
    assert updated.status == "Off Duty"
    assert updated.current_location == "Coffee Shop"


def test_update_resident_street():
    add_street("Old Street")
    add_street("New Street")
    resident = add_resident("mover", "pass", "Old Street")

    assert resident.street.name == "Old Street"

    # Test update
    update_resident_street(resident.id, "New Street")

    # Refetch resident to confirm change
    updated_resident = get_resident_by_id(resident.id)
    assert updated_resident.street.name == "New Street"

    # Test invalid street
    with pytest.raises(ValueError, match="Street 'Fake Street' not found"):
        update_resident_street(resident.id, "Fake Street")


def test_get_resident_inbox_no_drives_returns_message():
    add_street("No Drive Street")
    resident = add_resident("resident_no_drive", "password", "No Drive Street")

    inbox = get_resident_inbox(resident.id)
    assert len(inbox) == 1
    assert "No upcoming drives" in inbox[0]


def test_add_duplicates_are_prevented():
    # Street duplicates
    street = add_street("Dupe Street")
    assert street is not None
    with pytest.raises(ValueError, match="Street 'Dupe Street' already exists"):
        add_street("Dupe Street")

    # Driver duplicates
    driver = add_driver("duplicate_driver", "password")
    assert driver is not None
    with pytest.raises(ValueError, match="Driver 'duplicate_driver' already exists"):
        add_driver("duplicate_driver", "password")

    # Resident duplicates
    add_street("Pine Street")
    resident = add_resident("duplicate_resident", "password", "Pine Street")
    assert resident is not None
    with pytest.raises(
        ValueError, match="Resident 'duplicate_resident' already exists"
    ):
        add_resident("duplicate_resident", "password", "Pine Street")
