import pytest
from unittest.mock import patch, MagicMock
from App.main import create_app
from App.database import db, create_db
from App.models import Drive, User, Driver, Resident, Street, StopRequest
from App.controllers import (
    schedule_drive,
    get_resident_inbox,
    request_stop,
    get_stop_requests_for_driver,
    update_driver_status,
    get_driver_status_and_location,
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
#                               Unit Tests
# =============================================================================


def test_new_user():
    user = User(username="bob", password="bobpass")
    assert user.username == "bob"


def test_user_json():
    user = User(username="bob", password="bobpass")
    user_json = user.get_json()
    assert user_json == {"id": None, "username": "bob"}


def test_set_password():
    password = "mypassword"
    user = User(username="test", password=password)
    assert (
        user.password != password
    )  # Password should be hashed, not stored as plaintext


def test_check_password():
    password = "mypassword"
    user = User(username="test", password=password)
    assert user.check_password(password)  # Correct password should pass
    assert not user.check_password("notmypassword")  # Wrong password should fail


def test_new_driver():
    driver = User(username="driver1", password="driverpass")
    assert driver.username == "driver1"


def test_driver_json():
    driver = User(username="driver1", password="driverpass")
    driver_json = driver.get_json()
    assert driver_json == {"id": None, "username": "driver1"}


def test_new_resident():
    resident = User(username="resident1", password="residentpass")
    assert resident.username == "resident1"


def test_resident_json():
    resident = User(username="resident1", password="residentpass")
    resident_json = resident.get_json()
    assert resident_json == {"id": None, "username": "resident1"}


def test_new_street():
    street = Street(name="Main Street")
    assert street.name == "Main Street"


def test_street_json():
    street = Street(name="Main Street")
    street_json = street.get_json()
    assert street_json == {"id": None, "name": "Main Street"}


def test_new_drive():
    drive = Drive(driver_id=1, street_id=2, scheduled_time="2025-10-10 10:00")
    assert drive.driver_id == 1
    assert drive.street_id == 2
    assert drive.scheduled_time == "2025-10-10 10:00"


def test_drive_json():
    drive = Drive(driver_id=1, street_id=2, scheduled_time="2025-10-10 10:00")
    drive_json = drive.get_json()
    assert drive_json == {
        "id": None,
        "driver_id": 1,
        "street_id": 2,
        "scheduled_time": "2025-10-10 10:00",
    }


def test_new_stop_request():
    stop_request = StopRequest(
        resident_id=1, drive_id=2, message="Stop by the red house."
    )
    assert stop_request.resident_id == 1
    assert stop_request.drive_id == 2
    assert stop_request.message == "Stop by the red house."


def test_stop_request_json():
    stop_request = StopRequest(
        resident_id=1, drive_id=2, message="Stop by the red house."
    )
    stop_request_json = stop_request.get_json()
    assert stop_request_json == {
        "id": None,
        "resident_id": 1,
        "drive_id": 2,
        "message": "Stop by the red house.",
    }


@patch("App.database.db.session.get")
def test_schedule_drive_invalid_driver(mock_db_get):
    mock_db_get.return_value = None
    with pytest.raises(ValueError, match="Driver not found"):
        schedule_drive(999, "Real Street", "2025-10-10 10:00")


@patch("App.models.Street.query")
@patch("App.database.db.session.get")
def test_schedule_drive_invalid_street(mock_db_get, mock_street_query):
    mock_db_get.return_value = MagicMock(id=1, username="driver")
    mock_street_query.filter_by.return_value.first.return_value = None
    with pytest.raises(ValueError, match="Street 'Fake Street' not found"):
        schedule_drive(1, "Fake Street", "2025-10-10 10:00")


@patch("App.models.Street.query")
@patch("App.database.db.session.get")
def test_schedule_drive_invalid_date_format(mock_db_get, mock_street_query):
    mock_db_get.return_value = MagicMock(id=1, username="driver")
    mock_street_query.filter_by.return_value.first.return_value = MagicMock(id=1)
    with pytest.raises(ValueError, match="Invalid time format"):
        schedule_drive(1, "Real Street", "not-a-date")


@patch("App.models.Driver.query")
def test_get_stop_requests_invalid_driver(mock_driver_query):
    mock_driver_query.options.return_value.get.return_value = None
    with pytest.raises(ValueError, match="Driver not found"):
        get_stop_requests_for_driver(999)


@patch("App.models.Driver.query")
def test_update_driver_status_invalid_driver(mock_driver_query):
    mock_driver_query.get.return_value = None
    with pytest.raises(ValueError, match="Driver not found"):
        update_driver_status(999, "On Duty", "New Location")


@patch("App.models.Resident.query")
@patch("App.models.Drive.query")
def test_request_stop_wrong_street(mock_drive_query, mock_resident_query):
    mock_resident = MagicMock(id=5, street_id=10)
    mock_drive = MagicMock(id=8, street_id=99, driver=MagicMock(username="bakery"))
    mock_resident_query.get.return_value = mock_resident
    mock_drive_query.options.return_value.get.return_value = mock_drive
    with pytest.raises(
        ValueError, match="You can only request stops for drives on your street"
    ):
        request_stop(5, 8, "A message")


@patch("App.models.Resident.query")
def test_request_stop_invalid_resident(mock_resident_query):
    mock_resident_query.get.return_value = None
    with pytest.raises(ValueError, match="Resident not found"):
        request_stop(999, 1, "A message")


@patch("App.models.Resident.query")
@patch("App.models.Drive.query")
def test_request_stop_invalid_drive(mock_drive_query, mock_resident_query):
    mock_resident_query.get.return_value = MagicMock(id=1, street_id=1)
    mock_drive_query.options.return_value.get.return_value = None
    with pytest.raises(ValueError, match="Drive not found"):
        request_stop(1, 999, "A message")


@patch("App.models.Resident.query")
def test_get_resident_inbox_invalid_resident(mock_resident_query):
    mock_resident_query.get.return_value = None
    with pytest.raises(ValueError, match="Resident not found"):
        get_resident_inbox(999)


@patch("App.database.db.session.get")
def test_get_driver_status_invalid_driver(mock_db_get):
    mock_db_get.return_value = None
    with pytest.raises(ValueError, match="Driver not found"):
        get_driver_status_and_location(999)
