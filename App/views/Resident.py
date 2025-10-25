from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.controllers import get_resident_inbox, request_stop
from App.controllers.Resident import (
    get_all_residents_summary,
    get_driver_status_and_location,
)
from App.models import Resident
from App.utils.validation import *

# Create a Blueprint for resident views
resident_views = Blueprint("resident_views", __name__, template_folder="../templates")


# Route to get a summary of all residents
@resident_views.route("/api/residents", methods=["GET"])
def get_residents_summary_route():
    """Provides a summary list of all residents."""
    residents = get_all_residents_summary()
    return jsonify(residents), 200


# Route for a resident to view their inbox
@resident_views.route("/api/residents/inbox", methods=["GET"])
@jwt_required()
def get_resident_inbox_route():
    """Allows an authenticated resident to view their inbox."""
    current_user_id = get_jwt_identity()
    resident = Resident.query.get(current_user_id)

    if not resident or resident.role != "resident":
        return jsonify({"Error": "Access forbidden: Residents only"}), 403

    try:
        inbox_items = get_resident_inbox(resident.id)
        return jsonify(inbox_items), 200
    except ValueError as e:
        return jsonify({"Error": str(e)}), 404


# Route for a resident to request a stop
@resident_views.route("/api/residents/request-stop", methods=["POST"])
@jwt_required()
def request_stop_route():
    """Allows an authenticated resident to request a stop with validation."""
    current_user_id = get_jwt_identity()
    resident = Resident.query.get(current_user_id)

    if not resident or resident.role != "resident":
        return jsonify({"errors": ["Access forbidden: Residents only"]}), 403

    data = request.get_json()
    drive_id = data.get("drive_id")
    message = data.get("message")

    # Validate all fields
    validation_errors = combine_validation_errors(
        check_id(drive_id, "Drive ID"),
        check_required(message, "Message"),
        check_string_length(message, "Message", max_length=200),
    )

    if validation_errors:
        return jsonify({"errors": validation_errors}), 400

    try:
        result = request_stop(resident.id, drive_id, message)
        return jsonify({"message": result}), 201
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400


# Route for Resident to view a specific driver's status
@resident_views.route(
    "/api/resident/driver-status-and-location/<int:driver_id>/status", methods=["GET"]
)
@jwt_required()
def get_driver_status_route(driver_id):
    """Provides the status and location for a specific driver."""
    current_user_id = get_jwt_identity()
    resident = Resident.query.get(current_user_id)

    if not resident or resident.role != "resident":
        return jsonify({"Error": "Access forbidden: Residents only"}), 403
    try:
        status = get_driver_status_and_location(driver_id)
        return jsonify({"Status": status}), 200
    except ValueError as e:
        return jsonify({"Error": str(e)}), 404
