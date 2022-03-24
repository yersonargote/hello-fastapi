# Python imports
from typing import Optional

# Local imports
from data import users
from models import User
from password import generate_token, verify_password


def authenticate(email: str, password: str) -> Optional[User]:
    """ authenticate

    parameters:
        email: email from the user.
        password: password from the user.
    return:
        user: returns authenticated user.
    """
    for user in users.values():
        if user.email == email and verify_password(password, user.password):
            return user
    return None


def create_access() -> str:
    """
    create access token

    returns: created str token. 
    """
    return generate_token()
