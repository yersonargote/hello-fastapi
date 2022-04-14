# Python imports
from typing import Optional, cast
# From fastapi
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.security.oauth2 import OAuth2PasswordBearer
from starlette import status
# From tortoise
from tortoise.exceptions import DoesNotExist
from tortoise import timezone
# Local imports
from password import verify_password
from models import (
    AccessToken,
    AccessTokenTortoise,
    User,
    UserTortoise
)


async def get_current_user(
        token: str = Depends(OAuth2PasswordBearer(tokenUrl="/token"))
    ) -> UserTortoise:
    """
    Get current user from token and return UserTortoise object.
    """
    try:
        access_token: AccessTokenTortoise = await AccessTokenTortoise.get(
            access_token = token, expiration_date__gte=timezone.now()
        ).prefetch_related("user")
        return cast(UserTortoise, access_token.user)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


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
