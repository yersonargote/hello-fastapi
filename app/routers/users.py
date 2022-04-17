# From fastapi
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from starlette import status
# From tortoise
from tortoise.exceptions import IntegrityError
# From local
from app.models.auth import AccessToken
from app.models.user import User, UserPydantic, UserPydanticList, UserTortoise
from app.auth import authenticate, create_access_token, get_current_user
from app.password import get_password_hash


router = APIRouter()


@router.post(
    path="/token",
    status_code=status.HTTP_200_OK,
    tags=["login"]
)
async def create_token(
    form_data: OAuth2PasswordRequestForm = Depends(
        OAuth2PasswordRequestForm)
):
    """
    Create token.
    """
    email = form_data.username
    password = form_data.password

    user = await authenticate(email=email, password=password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    token: AccessToken = await create_access_token(user)
    return {"access_token": token.access_token, "token_type": "bearer"}

@router.get(
    path="/users/",
    status_code=status.HTTP_200_OK,
    response_model=UserPydanticList,
    dependencies=[Depends(get_current_user)],
    tags=["users"]
)
async def get_all_users() -> UserPydanticList:
    """
    Get all users.
    
    This path operation returns all user from the users table.
    
    No parameters.

    Returns a list with the information of each user.
    """
    users = await UserPydanticList.from_queryset(UserTortoise.all())
    return users
    # users = await asyncio.gather(UserTortoise.all())
    # return [User.from_orm(user) for user in users]


@router.post(
    path="/users/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserPydantic,
    tags=["users"]
)
async def create_user(user: User) -> UserPydantic:
    """
    Create user.

    This path operation create a user in the users table.

    Parameters:
        user: User to be added to users table.
    
    Returns:
        user: User has been added to users table.
    """
    user.password = get_password_hash(user.password)
    try:
        user_tortoise = await UserTortoise.create(
            **user.dict()
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exist."
        )
    # return User.from_orm(user_tortoise)
    return await UserPydantic.from_tortoise_orm(user_tortoise)


@router.get(
    path="/users/{id}",
    status_code=status.HTTP_200_OK,
    response_model=UserPydantic,
    dependencies=[Depends(get_current_user)],
    tags=["users"]
)
async def get_user(id: str = Path(...)) -> UserPydantic:
    """
    Get user.

    This path operation returns the user with the id specified in the path.

    Parameters:
        id: Id of the user to be returned.

    Returns:
        user: User with the id specified in the path.
    """
    user = await UserTortoise.get(id=id)
    return await UserPydantic.from_tortoise_orm(user)


@router.put(
    path="/user/{id}",
    status_code=status.HTTP_200_OK,
    response_model=UserPydantic,
    dependencies=[Depends(get_current_user)],
    tags=["users"]
)
async def update_user(
    id: str = Path(...),
    user: User= Body(...),
):
    user.password = get_password_hash(user.password)
    user_tortoise = await UserTortoise.get_or_none(id=id)
    if not user_tortoise:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="NOT FOUND.")
    await user_tortoise.update_from_dict(user.dict(exclude={"id"}, exclude_unset=True)).save()
    return await UserPydantic.from_tortoise_orm(user_tortoise)
