# From pydantic
from pydantic.fields import Field
from pydantic.main import BaseModel
# Form tortoise
from tortoise.contrib.pydantic.creator import pydantic_model_creator, pydantic_queryset_creator
from tortoise.fields.data import CharField
from tortoise.models import Model


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


UserPydantic = pydantic_model_creator(UserTortoise)
UserPydanticList = pydantic_queryset_creator(UserTortoise)
