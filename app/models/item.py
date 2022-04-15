# From python
from typing import Optional
# From pydantic
from pydantic.fields import Field
from pydantic.main import BaseModel
# From tortoise
from tortoise.contrib.pydantic.creator import pydantic_model_creator, pydantic_queryset_creator
from tortoise.fields.data import CharField, FloatField, IntField
from tortoise.models import Model
from tortoise.validators import MaxValueValidator, MinValueValidator


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


ItemPydantic = pydantic_model_creator(ItemTortoise)
ItemPydanticList = pydantic_queryset_creator(ItemTortoise)
