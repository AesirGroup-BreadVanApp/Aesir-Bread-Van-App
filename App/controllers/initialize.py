from .user import create_user
from .Resident import add_resident
from .Driver import add_driver
from .Street import add_street
from .Driver import schedule_drive
from .Resident import request_stop
from App.database import db
from datetime import datetime, timedelta


def initialize():
    db.drop_all()
    db.create_all()

    # Add Streets
    main_street = add_street("Main Street")
    park_avenue = add_street("Park Avenue")
    elm_street = add_street("Elm Street")
    oak_road = add_street("Oak Road")

    # Add Drivers
    driver_bob = add_driver(
        "Bob the Baker", "bobpass", status="On Duty", current_location="Main Street"
    )
    driver_alice = add_driver(
        "Alice the Patissier",
        "alicepass",
        status="Off Duty",
        current_location="Park Avenue",
    )
    driver_john = add_driver(
        "John the Breadman", "johnpass", status="On Duty", current_location="Elm Street"
    )

    # Add Residents
    resident_charlie = add_resident("Charlie", "charliepass", "Main Street")
    resident_diana = add_resident("Diana", "dianapass", "Park Avenue")
    resident_emily = add_resident("Emily", "emilypass", "Elm Street")
    resident_frank = add_resident("Frank", "frankpass", "Oak Road")

    # Schedule Drives
    now = datetime.now()
    schedule_drive(
        driver_bob.id,
        "Main Street",
        (now + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"),
    )
    schedule_drive(
        driver_alice.id,
        "Park Avenue",
        (now + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
    )
    schedule_drive(
        driver_john.id,
        "Elm Street",
        (now + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
    )

    # Add Stop Requests
    request_stop(
        resident_charlie.id, 1, "Please stop near the grey house with the red door."
    )
    request_stop(
        resident_diana.id,
        2,
        "I need bread for dinner, stop near the second house on the right.",
    )
    request_stop(
        resident_emily.id,
        3,
        "Could you stop by the park entrance? I will be waiting there.",
    )
