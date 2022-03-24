# Pydantic imports
from pydantic import BaseModel, Field
from typing import Optional


class Item(BaseModel):
    """
    Item model

    Attributes:
        id: Unique identifier for the item
        name: Name of the item
        description: Description of the item
        price: Price of the item
        stock: Stock of the item
    """
    id: str = Field(..., title="The item's unique ID")
    name: str = Field(..., min_length=2, max_length=50,
                      title="The item's name")
    description: Optional[str] = Field(
        None, min_length=3, max_length=500, title="The item's description")
    price: float = Field(..., gt=0, le=100000000, title="The item's price")
    stock: int = Field(..., gt=0, le=100, title="The item's stock")


class User(BaseModel):
    """
    User model

    Attributes:
        id: Unique identifier for the user
        email: Email of the user
        password: Password of the user
        access_token: Access token of the user
    """
    id: str = Field(..., title="The user's unique ID")
    email: str = Field(..., title="The user's email address")
    password: str = Field(..., title="The user's password")
    access_token: str = Field(..., title="The access token")
