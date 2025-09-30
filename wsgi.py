import click, pytest, sys
from flask.cli import with_appcontext, AppGroup
from App.database import db, get_migrate
from App.models import User
from App.main import create_app
from App.controllers import (
    create_user,
    get_all_users_json,
    get_all_users,
    get_all_residents,
    get_all_residents_summary,
    get_all_drivers,
    get_all_drivers_summary,
    initialize,
    add_driver,
    schedule_drive,
    get_stop_requests_for_driver,
    update_driver_status,
    add_resident,
    get_resident_inbox,
    request_stop,
    get_driver_status_and_location,
)


app = create_app()
migrate = get_migrate(app)


@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
    print("database intialized")


# --- User Commands ---
user_cli = AppGroup("user", help="User object commands")


@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    create_user(username, password)
    print(f"{username} created!")


@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == "string":
        print(get_all_users())
    else:
        print(get_all_users_json())


app.cli.add_command(user_cli)


# --- Driver Commands ---
driver_cli = AppGroup("driver", help="Driver object commands")


@driver_cli.command("create", help="Creates a driver")
@click.argument("name", default="lequisha")
@click.argument("password", default="lequishapass")
def create_driver_command(name, password):
    add_driver(name, password)
    print(f"Driver: {name} created!")


@driver_cli.command("list", help="Lists drivers in the database")
def list_driver_command():
    drivers = get_all_drivers_summary()
    print_list_neatly(drivers, heading=" Available Drivers ")


@driver_cli.command("schedule", help="Schedules a drive for a driver")
def schedule_drive_command():
    drivers = get_all_drivers_summary()
    print_list_neatly(drivers, heading=" Select a Driver ")
    try:
        driver_id = int(input("Enter the ID of the driver to schedule: "))
        street_name = input("Enter the street name: ")
        time_str = input("Enter the time (YYYY-MM-DD HH:MM): ")

        result = schedule_drive(driver_id, street_name, time_str)
        print(result)
    except ValueError as e:
        click.echo(f"\nError: {e}")
    except Exception:
        click.echo("\nAn unexpected error occurred. Please check your inputs.")


@driver_cli.command("view_requests", help="View stop requests for a driver")
def view_stop_requests_command():
    drivers = get_all_drivers_summary()
    print_list_neatly(drivers, heading=" Select a Driver ")
    try:
        driver_id = int(input("Enter the ID of the driver to view stop requests: "))
        requests = get_stop_requests_for_driver(driver_id)
        print_list_neatly(requests, heading=" Stop Requests ")
    except ValueError as e:
        click.echo(f"\nError: {e}")
    except Exception:
        click.echo("\nAn unexpected error occurred. Please check your inputs.")


@driver_cli.command("update_status", help="Updates a driver's status and location")
def update_driver_status_command():
    drivers = get_all_drivers_summary()
    print_list_neatly(drivers, heading=" Select a Driver ")
    try:
        driver_id = int(input("Enter the ID of the driver to update: "))
        new_status = input("Enter the new status: ")
        new_location = input("Enter the new location: ")
        result = update_driver_status(driver_id, new_status, new_location)
        print(result)
    except ValueError as e:
        click.echo(f"\nError: {e}")
    except Exception:
        click.echo("\nAn unexpected error occurred. Please check your inputs.")


app.cli.add_command(driver_cli)


# --- Resident Commands ---
resident_cli = AppGroup("resident", help="Resident object commands")


@resident_cli.command("create", help="Creates a resident")
@click.argument("name", default="carlton")
@click.argument("password", default="carltonpass")
@click.argument("street_name", default="Main Street")
def create_resident_command(name, password, street_name):
    try:
        add_resident(name, password, street_name)
        print(f"Resident: {name} created!")
    except ValueError as e:
        click.echo(f"\nError: {e}")


@resident_cli.command("list", help="Lists residents in the database")
def list_resident_command():
    residents = get_all_residents_summary()
    print_list_neatly(residents, heading=" Available Residents ")


@resident_cli.command("inbox", help="Shows the inbox of a resident")
def resident_inbox_command():
    residents = get_all_residents_summary()
    print_list_neatly(residents, heading=" Select a Resident ")
    try:
        resident_id = int(input("Enter the ID of the resident to view their inbox: "))
        inbox = get_resident_inbox(resident_id)
        print_list_neatly(inbox, heading=" Resident Inbox ")
    except ValueError as e:
        click.echo(f"\nError: {e}")


@resident_cli.command("request_stop", help="Request a stop for a drive")
def request_stop_command():
    residents = get_all_residents_summary()
    print_list_neatly(residents, heading=" Select a Resident ")
    try:
        resident_id = int(input("Enter the ID of the resident making the request: "))
        inbox = get_resident_inbox(resident_id)

        if not inbox or "No upcoming drives" in inbox[0]:
            print("\nNo drives available to request a stop for.")
            return

        print_list_neatly(inbox, heading=" Select a Drive to Stop ")
        drive_id = int(input("Enter the ID of the drive to stop: "))
        message = input("Enter a message for the request: ")
        result = request_stop(resident_id, drive_id, message)
        print(result)
    except ValueError as e:
        click.echo(f"\nError: {e}")
    except Exception:
        click.echo("\nAn unexpected error occurred. Please check your inputs.")


@resident_cli.command(
    "get_driver_status_and_location", help="Get the status and location of a driver"
)
def driver_status_and_location_command():
    drivers = get_all_drivers_summary()
    print_list_neatly(drivers, heading=" Select a Driver to Check ")
    try:
        driver_id = int(input("Enter the ID of the driver to check status: "))
        status = get_driver_status_and_location(driver_id)
        print("\n---------------- Driver Status -----------------")
        print(status)
        print("----------------------------------------------")
    except ValueError as e:
        click.echo(f"\nError: {e}")


app.cli.add_command(resident_cli)


# --- Test Commands ---
test = AppGroup("test", help="Testing commands")


@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))


app.cli.add_command(test)


def print_list_neatly(items, heading=" Items "):
    if not items:
        print(f"\n--- {heading.strip()} ---")
        print("No items to display.")
        print("-" * (len(heading) + 4) + "\n")
        return

    item_strings = [str(item) for item in items]
    max_item_length = max(len(s) for s in item_strings)
    heading_length = max(len(heading), max_item_length, 30)

    print("\n" + heading.center(heading_length, "-"))
    for item in item_strings:
        print(item)
    print("-" * heading_length + "\n")
