# Python imports
from typing import Optional

from tortoise.exceptions import DoesNotExist

# Local imports
from password import verify_password
from models import (
    AccessToken,
    AccessTokenTortoise,
    User,
    UserTortoise
)


async def authenticate(email: str, password: str) -> Optional[User]:
    """ authenticate

    parameters:
        email: email from the user.
        password: password from the user.
    return:
        user: returns authenticated user.
    """
    try:
        user = await UserTortoise.get(email=email)
    except DoesNotExist:
        return None

    if not verify_password(password, user.password):
        return None
    return User.from_orm(user)


async def create_access_token(user: User) -> AccessToken:
    """
    create access token

    returns: created Access Token. 
    """
    access_token = AccessToken(user_id=user.id)
    access_token_tortoise = await AccessTokenTortoise.create(**access_token.dict())
    return AccessToken.from_orm(access_token_tortoise)
