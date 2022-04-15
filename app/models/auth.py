# From python
from datetime import datetime, timedelta
# From pydantic
from pydantic.fields import Field
from pydantic.main import BaseModel
# from tortoise
from tortoise import timezone
from tortoise.fields.data import CharField, DatetimeField
from tortoise.fields.relational import ForeignKeyField
from tortoise.models import Model
# From local
from app.password import generate_token


def get_expiration_date(duration_seconds: int = 86400) -> datetime:
    return timezone.now() + timedelta(seconds=duration_seconds)


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
