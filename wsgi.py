import sys
import click
import pytest
from flask.cli import AppGroup
from App.main import create_app
from App.database import get_migrate
from App.controllers import (
    initialize,
    create_user,
    get_all_users_json,
    get_all_users,
    get_all_residents_summary,
    get_all_drivers_summary,
    add_driver,
    schedule_drive,
    get_stop_requests_for_driver,
    update_driver_status,
    add_resident,
    get_resident_inbox,
    request_stop,
    get_driver_status_and_location,
    get_all_streets,
)

# --- Flask app setup ---
app = create_app()
migrate = get_migrate(app)


# ===========================================================
# INIT COMMAND
# ===========================================================
@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
    click.echo("Database initialized successfully.")


# ===========================================================
# USER COMMANDS
# ===========================================================
user_cli = AppGroup("user", help="User object commands")


@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    create_user(username, password)
    click.echo(f"User '{username}' created!")


@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == "string":
        click.echo(get_all_users())
    else:
        click.echo(get_all_users_json())


app.cli.add_command(user_cli)


# ===========================================================
# DRIVER COMMANDS
# ===========================================================
driver_cli = AppGroup("driver", help="Driver object commands")


@driver_cli.command("create", help="Creates a driver")
@click.argument("name", default="lequisha")
@click.argument("password", default="lequishapass")
def create_driver_command(name, password):
    add_driver(name, password)
    click.echo(f"Driver '{name}' created!")


@driver_cli.command("list", help="Lists drivers in the database")
def list_driver_command():
    print_list_neatly(get_all_drivers_summary(), heading="Available Drivers")


@driver_cli.command("schedule", help="Schedules a drive for a driver")
def schedule_drive_command():
    try:
        drivers = get_all_drivers_summary()
        print_list_neatly(drivers, heading="Select a Driver")
        driver_id = int(input("Enter driver ID: "))
        streets = get_all_streets()
        print_list_neatly(streets, heading="Available Streets")
        street_name = input("Enter street name: ")
        time_str = input("Enter the time (YYYY-MM-DD HH:MM): ")
        click.echo(schedule_drive(driver_id, street_name, time_str))
    except Exception as e:
        click.echo(f"Error: {e}")


@driver_cli.command("view_requests", help="View stop requests for a driver")
def view_stop_requests_command():
    try:
        drivers = get_all_drivers_summary()
        print_list_neatly(drivers, heading="Select a Driver")
        driver_id = int(input("Enter driver ID: "))
        print_list_neatly(
            get_stop_requests_for_driver(driver_id), heading="Stop Requests"
        )
    except Exception as e:
        click.echo(f"Error: {e}")


@driver_cli.command("update_status", help="Updates a driver's status and location")
def update_driver_status_command():
    try:
        drivers = get_all_drivers_summary()
        print_list_neatly(drivers, heading="Select a Driver")
        driver_id = int(input("Enter driver ID: "))
        new_status = input("Enter new status: ")
        new_location = input("Enter new location: ")
        click.echo(update_driver_status(driver_id, new_status, new_location))
    except Exception as e:
        click.echo(f"Error: {e}")


app.cli.add_command(driver_cli)


# ===========================================================
# RESIDENT COMMANDS
# ===========================================================
resident_cli = AppGroup("resident", help="Resident object commands")


@resident_cli.command("create", help="Creates a resident")
def create_resident_command():
    try:
        name = input("Enter resident name: ")
        password = input("Enter resident password: ")
        streets = get_all_streets()
        print_list_neatly(streets, heading="Available Streets")
        street_name = input("Enter street name: ")
        add_resident(name, password, street_name)
        click.echo(f"Resident '{name}' created!")
    except ValueError as e:
        click.echo(f"Error: {e}")


@resident_cli.command("list", help="Lists residents in the database")
def list_resident_command():
    print_list_neatly(get_all_residents_summary(), heading="Available Residents")


@resident_cli.command("inbox", help="Shows a resident's inbox")
def resident_inbox_command():
    try:
        residents = get_all_residents_summary()
        print_list_neatly(residents, heading="Select a Resident")
        resident_id = int(input("Enter resident ID: "))
        print_list_neatly(get_resident_inbox(resident_id), heading="Resident Inbox")
    except Exception as e:
        click.echo(f"Error: {e}")


@resident_cli.command("request_stop", help="Request a stop for a drive")
def request_stop_command():
    try:
        residents = get_all_residents_summary()
        print_list_neatly(residents, heading="Select a Resident")
        resident_id = int(input("Enter resident ID: "))
        inbox = get_resident_inbox(resident_id)
        if not inbox or "No upcoming drives" in inbox[0]:
            click.echo("No drives available to request a stop for.")
            return
        print_list_neatly(inbox, heading="Select a Drive")
        drive_id = int(input("Enter drive ID: "))
        message = input("Enter request message: ")
        click.echo(request_stop(resident_id, drive_id, message))
    except Exception as e:
        click.echo(f"Error: {e}")


@resident_cli.command("driver_status", help="Get a driver's status and location")
def driver_status_and_location_command():
    try:
        drivers = get_all_drivers_summary()
        print_list_neatly(drivers, heading="Select a Driver to Check")
        driver_id = int(input("Enter driver ID: "))
        status = get_driver_status_and_location(driver_id)
        click.echo("\n------ Driver Status ------")
        click.echo(status)
        click.echo("---------------------------")
    except Exception as e:
        click.echo(f"Error: {e}")


app.cli.add_command(resident_cli)


# ===========================================================
# TEST COMMANDS
# ===========================================================

test = AppGroup("test", help="Testing commands")


@test.command("all", help="Run all tests (unit and integration)")
def run_all_tests_command():
    """Runs pytest on the entire tests directory."""
    print("Running all tests...")
    # Point pytest to the tests directory
    exit_code = pytest.main(["App/tests"])
    sys.exit(exit_code)


@test.command("unit", help="Run only unit tests")
def run_unit_tests_command():
    """Runs pytest specifically on the test_unit.py file."""
    print("Running unit tests...")
    exit_code = pytest.main(["App/tests/test_unit.py"])
    sys.exit(exit_code)


@test.command("integration", help="Run only integration tests")
def run_integration_tests_command():
    """Runs pytest specifically on the test_integration.py file."""
    print("Running integration tests...")
    exit_code = pytest.main(["App/tests/test_integration.py"])
    sys.exit(exit_code)


app.cli.add_command(test)


# ===========================================================
# UTILITY
# ===========================================================
def print_list_neatly(items, heading="Items"):
    if not items:
        click.echo(f"\n--- {heading.strip()} ---")
        click.echo("No items to display.")
        click.echo("-" * (len(heading) + 4) + "\n")
        return
    item_strings = [str(item) for item in items]
    max_item_length = max(len(s) for s in item_strings)
    heading_length = max(len(heading), max_item_length, 30)
    print("\n" + heading.center(heading_length, "-"))
    for item in item_strings:
        print(item)
    print("-" * heading_length + "\n")
