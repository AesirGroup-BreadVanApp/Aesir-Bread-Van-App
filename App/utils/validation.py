import re
from datetime import datetime


USERNAME_PATTERN = r"^[a-zA-Z0-9_ ]{3,30}$"
USERNAME_ERROR = "Username can only contain letters, numbers, spaces and underscores. (3-30 characters)."
MAX_USERNAME_LENGTH = 30

PASSWORD_PATTERN = r"^[a-zA-Z0-9!@#$%^&*()_+={}:;\"'<>?,./\\|`~]+$"
PASSWORD_ERROR = "Password can only contain letters, numbers, and special characters."
MAX_RAW_PASSWORD_LENGTH = 64


# Basic Check Functions (Return error string or None)


def check_required(value, field_name="Field"):
    if value is None or (isinstance(value, str) and not value.strip()):
        return f"{field_name} cannot be empty."
    return None


def check_string_type(value, field_name="Field"):
    if not isinstance(value, str):
        return f"{field_name} must be a string."
    return None


def check_string_length(value, field_name="Field", min_length=1, max_length=None):
    if not isinstance(value, str):
        return f"{field_name} must be a string."
    length = len(value)
    if min_length and length < min_length:
        return f"{field_name} must be at least {min_length} characters."
    if max_length and length > max_length:
        return f"{field_name} must be no more than {max_length} characters."
    return None


def check_regex(value, pattern, field_name="Field", error_message="Invalid format."):
    if not isinstance(value, str) or not re.fullmatch(pattern, value):
        return f"{field_name}: {error_message}"
    return None


def check_id(value, field_name="ID"):
    if not isinstance(value, int) or value <= 0:
        return f"{field_name} must be a positive integer."
    return None


def check_time_format(value, field_name="Time"):
    if not isinstance(value, str):
        return f"{field_name} must be a string."
    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError:
        return f"{field_name}: Invalid time format. Use 'YYYY-MM-DD HH:MM'."
    return None


def check_driver_status(value, field_name="Status"):
    allowed_values = {"On Duty", "Off Duty", "On Break"}
    if value not in allowed_values:
        options = ", ".join(f"'{val}'" for val in allowed_values)
        return f"{field_name} must be one of: {options}."
    return None


# ============================================================
# FIELD-SPECIFIC VALIDATION USING validate_field()
# ============================================================


def validate_username(username):
    return run_validations(
        check_required(username, "Username"),
        check_string_length(username, "Username", max_length=MAX_USERNAME_LENGTH),
        check_regex(username, USERNAME_PATTERN, "Username", USERNAME_ERROR),
    )


def validate_password(password):
    return run_validations(
        check_required(password, "Password"),
        check_string_length(
            password, "Password", min_length=7, max_length=MAX_RAW_PASSWORD_LENGTH
        ),
        check_regex(password, PASSWORD_PATTERN, "Password", PASSWORD_ERROR),
    )


def combine_validation_errors(*validation_results):
    """
    Combines multiple validation results into a single list of errors.
    Each validation_result should be a list of error messages.
    """
    errors = []
    for result in validation_results:
        if result:  # Only add non-empty error lists
            if isinstance(result, list):
                errors.extend(result)
            else:
                errors.append(result)
    return errors


def run_validations(*checks):
    """
    Runs multiple validation checks and returns a list of non-None error messages.
    Each check should be a function call that returns either an error string or None.
    """
    return [error for error in checks if error is not None]
