# Python imports
from typing import List

# FastAPI imports
from fastapi import Body, Depends, FastAPI, Path, Query, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import authenticate, create_access

# Local imports
from models import Item, User
from data import items, users
from password import get_password_hash


app = FastAPI()


def get_current_user(token: str = Depends(OAuth2PasswordBearer(
        tokenUrl="/token"))) -> User:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    for user in users.values():
        if user.access_token == token:
            return user
    return None


@app.get(
    path="/users/",
    status_code=status.HTTP_200_OK,
    response_model=List[User],
    dependencies=[Depends(get_current_user)],
)
def get_all_users() -> List[User]:
    """
    Get all users
    
    This path operation returns all user from the users dictionary.
    
    No parameters.

    Returns a list with the information of each user.
    """
    return list(users.values())


@app.post(
    path="/users/",
    status_code=status.HTTP_201_CREATED,
    response_model=User,
)
def create_user(user: User) -> User:
    """
    Create user.

    This path operation create a user and append to users dict.

    Parameters:
        - user: User to be added to users dict.
    
    Returns:
        - user: User has been added to users dict.
    """
    for u in users.values():
        if u.email == user.email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="User already exists")
    if user.id in users:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="User already exists")
    user.password = get_password_hash(user.password)
    user.access_token = create_access()
    users[user.id] = user
    return user


@app.get(
    path="/users/{id}",
    status_code=status.HTTP_200_OK,
    response_model=User,
    dependencies=[Depends(get_current_user)]
)
def get_user(user_id: str) -> User:
    if user_id not in users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    return users[user_id]


@app.post(
    path="/token",
    status_code=status.HTTP_200_OK
)
def create_token(
    form_data: OAuth2PasswordRequestForm = Depends(
        OAuth2PasswordRequestForm)
):
    email = form_data.username
    password = form_data.password
    user = authenticate(email=email, password=password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password")
    return {"access_token": user.access_token, "token_type": "bearer"}


@app.get(
    path="/items",
    status_code=status.HTTP_200_OK,
    response_model=List[Item],
    dependencies=[Depends(get_current_user)]
)
def read_all_items():
    return list(items.values())


@app.get(
    path="/items/{item_id}",
    status_code=status.HTTP_200_OK,
    response_model=Item,
)
def read_item(
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
