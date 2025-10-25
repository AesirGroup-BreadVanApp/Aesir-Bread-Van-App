from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.controllers import (
    schedule_drive,
    get_all_drivers_summary,
    update_driver_status,
    get_stop_requests_for_driver,
    get_driver_status_and_location,
)
from App.models import Driver
from App.utils.validation import *

# Create a Blueprint for driver views
driver_views = Blueprint("driver_views", __name__, template_folder="../templates")

MAX_STREET_NAME_LENGTH = 100


# Route to get a summary of all drivers
@driver_views.route("/api/drivers", methods=["GET"])
def get_drivers_summary_route():
    """Provides a summary list of all drivers."""
    drivers = get_all_drivers_summary()
    return jsonify(drivers), 200


# Route for a driver to schedule a drive
@driver_views.route("/api/drivers/schedule", methods=["POST"])
@jwt_required()
def schedule_drive_route():
    """Allows an authenticated driver to schedule a drive with validation."""
    current_user_id = get_jwt_identity()
    driver = Driver.query.get(current_user_id)

    if not driver or driver.role != "driver":
        return jsonify({"errors": ["Access forbidden: Drivers only"]}), 403

    data = request.get_json()
    street_name = data.get("street_name")
    time_str = data.get("time_str")

    # Validate all fields
    validation_errors = combine_validation_errors(
        check_required(street_name, "Street name"),
        check_string_length(
            street_name, "Street name", max_length=MAX_STREET_NAME_LENGTH
        ),
        check_time_format(time_str),
    )

    if validation_errors:
        return jsonify({"errors": validation_errors}), 400

    try:
        result = schedule_drive(driver.id, street_name, time_str)
        return jsonify({"message": result}), 201
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400


# Route for a driver to update their status
@driver_views.route("/api/drivers/status", methods=["PUT"])
@jwt_required()
def update_driver_status_route():
    """Allows an authenticated driver to update their status with validation."""
    current_user_id = get_jwt_identity()
    driver = Driver.query.get(current_user_id)

    if not driver or driver.role != "driver":
        return jsonify({"errors": ["Access forbidden: Drivers only"]}), 403

    data = request.get_json()
    new_status = data.get("status")
    new_location = data.get("location")

    # Validate all fields
    validation_errors = combine_validation_errors(
        check_driver_status(new_status),
        check_string_length(new_location, "Location", max_length=120),
    )

    if validation_errors:
        return jsonify({"errors": validation_errors}), 400

    try:
        result = update_driver_status(driver.id, new_status, new_location)
        return jsonify({"message": result}), 200
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400


# Route for a driver to view their stop requests
@driver_views.route("/api/drivers/requests", methods=["GET"])
@jwt_required()
def get_driver_requests_route():
    """Allows an authenticated driver to view their stop requests."""
    current_user_id = get_jwt_identity()
    driver = Driver.query.get(current_user_id)

    if not driver or driver.role != "driver":
        return jsonify({"Error": "Access forbidden: Drivers only"}), 403

    try:
        requests = get_stop_requests_for_driver(driver.id)
        return jsonify(requests), 200
    except ValueError as e:
        return jsonify({"Error": str(e)}), 400
