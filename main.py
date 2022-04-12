# Python imports
from typing import List, Union, cast

# FastAPI imports
from fastapi import Body, Depends, FastAPI, Path, Query, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise import timezone
from tortoise.contrib.fastapi import register_tortoise

# Local imports
from auth import authenticate, create_access_token
from config import TORTOISE_ORM
from data import items, users
from password import get_password_hash
from models import (
    AccessToken,
    AccessTokenTortoise,
    Item,
    User,
    UserPydantic,
    UserPydanticList,
    UserTortoise,
    ItemTortoise,
    ItemPydantic,
    ItemPydanticList,
)


app = FastAPI()


async def get_current_user(token: str = Depends(OAuth2PasswordBearer(
        tokenUrl="/token"))) -> UserTortoise:
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


@app.get(
    path="/users/",
    status_code=status.HTTP_200_OK,
    response_model=UserPydanticList,
    dependencies=[Depends(get_current_user)],
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


@app.post(
    path="/users/",
    status_code=status.HTTP_201_CREATED,
    response_model=User,
)
async def create_user(user: User) -> User:
    """
    Create user.

    This path operation create a user in the users table.

    Parameters:
        user: User to be added to users table.
    
    Returns:
        user: User has been added to users table.
    """
    for u in users.values():
        if u.email == user.email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="User already exists")
    if user.id in users:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="User already exists")
    user.password = get_password_hash(user.password)

    try:
        user_tortoise = await UserTortoise.create(
            **user.dict()
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exist."
        )
    return User.from_orm(user_tortoise)


@app.get(
    path="/users/{id}",
    status_code=status.HTTP_200_OK,
    response_model=UserPydantic,
    dependencies=[Depends(get_current_user)]
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


@app.post(
    path="/token",
    status_code=status.HTTP_200_OK
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


@app.get(
    path="/items",
    status_code=status.HTTP_200_OK,
    response_model=ItemPydanticList,
    dependencies=[Depends(get_current_user)]
)
async def read_all_items():
    items = await ItemPydanticList.from_queryset(ItemTortoise.all())
    return items


@app.get(
    path="/items/{id}",
    status_code=status.HTTP_200_OK,
    response_model=ItemPydantic,
    dependencies=[Depends(get_current_user)]
)
async def read_item(
    id: str = Path(...)
):
    item = await ItemTortoise.get(id=id)
    return await ItemPydantic.from_tortoise_orm(item)


@app.post(
    path="/items/",
    status_code=status.HTTP_201_CREATED,
    response_model=Item,
    dependencies=[Depends(get_current_user)]
)
async def create_item(
    item: Item = Body(...)
):
    try:
        item_tortoise = await ItemTortoise.create(**item.dict())
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Item already exist."
        )
    return Item.from_orm(item_tortoise)


@app.put(
    path="/items/{item_id}",
    status_code=status.HTTP_200_OK,
    response_model=ItemPydantic,
    dependencies=[Depends(get_current_user)]
)
async def update_item(
    item_id: str = Path(...),
    item: Item = Body(...),
):
    item_tortoise = await ItemTortoise.get_or_none(id=item_id)
    if not item_tortoise:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="NOT FOUND.")
    await item_tortoise.update_from_dict(item.dict(exclude={"id"}, exclude_unset=True)).save()
    return await ItemPydantic.from_tortoise_orm(item_tortoise)


@app.get(
    path="/items/",
    status_code=status.HTTP_200_OK,
    response_model=ItemPydanticList,
    dependencies=[Depends(get_current_user)]
)
async def get_item_by_price(
    price: float = Query(...),
    limit: int = Query(default=10, gt=0, le=100),
):
    items_tortoise = await ItemTortoise.filter(price__gte=price).limit(limit)
    return items_tortoise


register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True
)
