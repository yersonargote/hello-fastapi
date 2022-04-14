# From fastapi
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path, Query
from starlette import status
# From tortoise
from tortoise.exceptions import IntegrityError
# From local
from auth import get_current_user
from models import Item, ItemPydantic, ItemPydanticList, ItemTortoise


router = APIRouter()


@router.get(
    path="/items",
    status_code=status.HTTP_200_OK,
    response_model=ItemPydanticList,
    dependencies=[Depends(get_current_user)]
)
async def read_all_items():
    items = await ItemPydanticList.from_queryset(ItemTortoise.all())
    return items


@router.get(
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


@router.post(
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


@router.put(
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


@router.get(
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
