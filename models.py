# Pydantic imports
from pydantic import BaseModel, Field

# Python libs
from typing import Optional
from datetime import datetime, timedelta

# Tortoise
from tortoise import timezone
from tortoise.models import Model
from tortoise.fields import CharField, ForeignKeyField
# from tortoise.fields.relational import ForeignKeyRelation
from tortoise.fields.data import DatetimeField, FloatField, IntField
from tortoise.contrib.pydantic.creator import pydantic_model_creator, pydantic_queryset_creator
from tortoise.validators import MinValueValidator, MaxValueValidator

# Local
from password import generate_token


def get_expiration_date(duration_seconds: int = 86400) -> datetime:
    return timezone.now() + timedelta(seconds=duration_seconds)


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
    price: float = Field(..., ge=0, le=100000000, title="The item's price")
    stock: int = Field(..., ge=0, le=10000, title="The item's stock")

    class Config:
        orm_mode = True


class ItemTortoise(Model):
    """
    Item model tortoise
    Attributes:
        id: Unique identifier for the item
        name: Name of the item
        description: Description of the item
        price: Price of the item
        stock: Stock of the item
    """
    id: str = CharField(pk=True, max_length=255)
    name: str = CharField(max_length=255, null=False, index=True)
    description: Optional[str] = CharField(max_length=500, null=True)
    price: float = FloatField(null=False, validators=[MinValueValidator(0), MaxValueValidator(100000000)])
    stock: int = IntField(null=False, validators=[MinValueValidator(0), MaxValueValidator(10000)])
    # TODO: Validators. Positive values in price and stock.

    class Meta:
        table = "items"


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

    class Config:
        orm_mode = True


class UserTortoise(Model):
    """
    User model tortoise

    Attributes:
        id: Unique identifier for the user
        email: Email of the user
        password: Password of the user
    """
    id: str = CharField(pk=True, max_length=255)
    email: str = CharField(index=True, unique=True, null=False, max_length=255)
    password: str = CharField(null=False, max_length=255)

    class Meta:
        table = "users"

    class PydanticMeta:
        exclude = ["password"]


class AccessToken(BaseModel):
    user_id: str = Field(max_length=255)
    access_token: str = Field(default_factory=generate_token)
    expiration_date: datetime = Field(default_factory=get_expiration_date)

    class Config:
        orm_mode = True


class AccessTokenTortoise(Model):
    """
    Access token tortoise

    Attributes:
        access_token: Access token of the user
        user: User related to the access token
        expiration_date: Date of expiration of the token
    """
    access_token = CharField(pk=True, max_length=255)
    user = ForeignKeyField("models.UserTortoise", null=False)
    expiration_date = DatetimeField(null=False)

    class Meta:
        table = "access_tokens"


UserPydantic = pydantic_model_creator(UserTortoise)
UserPydanticList = pydantic_queryset_creator(UserTortoise)
ItemPydantic = pydantic_model_creator(ItemTortoise)
ItemPydanticList = pydantic_queryset_creator(ItemTortoise)
