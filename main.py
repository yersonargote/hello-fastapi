# Python imports
from typing import List, cast

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
)


app = FastAPI()


async def get_current_user(token: str = Depends(OAuth2PasswordBearer(
        tokenUrl="/token"))) -> UserTortoise:
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
    Get all users
    
    This path operation returns all user from the users dictionary.
    
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
    user = await UserTortoise.get(id=id)
    return await UserPydantic.from_tortoise_orm(user)
    # return UserPydantic.from_tortoise_orm(User.from_orm(user_tortoise))


@app.post(
    path="/token",
    status_code=status.HTTP_200_OK
)
async def create_token(
    form_data: OAuth2PasswordRequestForm = Depends(
        OAuth2PasswordRequestForm)
):
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
    response_model=List[Item],
    dependencies=[Depends(get_current_user)]
)
async def read_all_items():
    return await UserTortoise.all()


@app.get(
    path="/items/{item_id}",
    status_code=status.HTTP_200_OK,
    response_model=Item,
)
async def read_item(
    item_id: str = Path(...)
):
    if item_id not in items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Item not found")
    return items[item_id]


@app.post(
    path="/items/",
    status_code=status.HTTP_201_CREATED,
    response_model=Item,
)
def create_item(
    item: Item = Body(...)
):
    if item.id in items.keys():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Item already exists",
        )
    items[item.id] = item
    return items[item.id]


@app.put(
    path="/items/{item_id}",
    status_code=status.HTTP_200_OK,
    response_model=Item,
)
def update_item(
    item_id: str = Path(...),
    item: Item = Body(...),
):
    if item_id not in items.keys():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    items[item_id] = item
    return items[item_id]


@app.get(
    path="/items/",
    status_code=status.HTTP_200_OK,
    response_model=List[Item],
)
def get_item_by_price(
    price: float = Query(...),
    limit: int = Query(..., gt=0, le=100),
):
    if price < 0 or limit < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid price or limit",
        )
    filter: List = [item for item in items.values() if item.price == price]
    return filter[:limit]


register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True
)


