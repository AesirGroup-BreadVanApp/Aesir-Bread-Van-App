from flask import (
    Blueprint,
    render_template,
    jsonify,
    request,
    send_from_directory,
    flash,
    redirect,
    url_for,
)
from flask_jwt_extended import jwt_required, current_user as jwt_current_user

from .index import index_views

from App.controllers import (
    create_user,
    get_all_users,
    get_all_users_json,
    jwt_required,
    add_driver,
    add_resident,
)

from App.utils.validation import *

user_views = Blueprint("user_views", __name__, template_folder="../templates")


@user_views.route("/users", methods=["GET"])
def get_user_page():
    users = get_all_users()
    return render_template("users.html", users=users)


@user_views.route("/users", methods=["POST"])
def create_user_action():
    data = request.form
    flash(f"User {data['username']} created!")
    create_user(data["username"], data["password"])
    return redirect(url_for("user_views.get_user_page"))


@user_views.route("/api/users", methods=["GET"])
def get_users_action():
    users = get_all_users_json()
    return jsonify(users)


@user_views.route("/api/users", methods=["POST"])
def create_user_endpoint():
    data = request.json
    user = create_user(data["username"], data["password"])
    return jsonify({"message": f"user {user.username} created with id {user.id}"})


@user_views.route("/static/users", methods=["GET"])
def static_user_page():
    return send_from_directory("static", "static-user.html")


# Route to create a new driver
@user_views.route("/api/users/driver", methods=["POST"])
def create_driver_endpoint():
    """Creates a new driver account with comprehensive validation."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    status = data.get("status", "Off Duty")
    location = data.get("location", "Unknown")

    # Collect all validation errors
    validation_errors = combine_validation_errors(
        validate_username(username),
        validate_password(password),
        check_driver_status(status),
        check_string_length(location, "Location", max_length=120),
    )

    if validation_errors:
        return jsonify({"errors": validation_errors}), 400

    try:
        new_driver = add_driver(username, password, status, location)
        return (
            jsonify(
                {
                    "message": f"Driver '{new_driver.username}' created with ID {new_driver.id}"
                }
            ),
            201,
        )
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400


# Route to create a new resident
@user_views.route("/api/users/resident", methods=["POST"])
def create_resident_endpoint():
    """Creates a new resident account with comprehensive validation."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    street_name = data.get("street_name")

    # Collect all validation errors
    validation_errors = combine_validation_errors(
        validate_username(username),
        validate_password(password),
        check_required(street_name, "Street name"),
        check_string_length(street_name, "Street name", max_length=100),
    )

    if validation_errors:
        return jsonify({"errors": validation_errors}), 400

    try:
        new_resident = add_resident(username, password, street_name)
        return (
            jsonify(
                {
                    "message": f"Resident '{new_resident.username}' created with ID {new_resident.id}"
                }
            ),
            201,
        )
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400
