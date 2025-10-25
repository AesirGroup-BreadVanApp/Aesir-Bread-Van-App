from App.models import User
from App.database import db
from App.utils.validation import (
    validate_username,
    validate_password,
    combine_validation_errors,
)


def create_user(username, password):
    """Create a new user with validation"""
    # Collect all validation errors
    validation_errors = combine_validation_errors(
        validate_username(username), validate_password(password)
    )

    if validation_errors:
        raise ValueError({"errors": validation_errors})

    # Continue with user creation if validation passes
    newuser = User(username=username, password=password)
    db.session.add(newuser)
    db.session.commit()
    return newuser


def get_user_by_username(username):
    result = db.session.execute(db.select(User).filter_by(username=username))
    return result.scalar_one_or_none()


def get_user(id):
    return db.session.get(User, id)


def get_all_users():
    return db.session.scalars(db.select(User)).all()


def get_all_users_json():
    users = get_all_users()
    if not users:
        return []
    users = [user.get_json() for user in users]
    return users


def update_user(id, username):
    user = get_user(id)
    if user:
        user.username = username
        # user is already in the session; no need to re-add
        db.session.commit()
        return True
    return None


def delete_user(id):
    # Delete a user from the database
    user = get_user(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    return None
