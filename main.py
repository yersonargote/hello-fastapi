from typing import List, Optional
from fastapi import Body, FastAPI, Path, Query, status, Response
from pydantic import BaseModel, Field
from typing import Dict


app = FastAPI()


class Item(BaseModel):
    id: str = Field(..., title="The item's unique ID")
    name: str = Field(..., min_length=2, max_length=50, title="The item's name")
    description: Optional[str] = Field(None, min_length=3, max_length=500, title="The item's description")
    price: float = Field(..., gt=0, le=100000000, title="The item's price")
    stock: int = Field(..., gt=0, le=100, title="The item's stock")


items: Dict[str, Item] = {}


@app.get(
    path="/items",
    status_code=status.HTTP_200_OK
)
def read_all_items():
    return items


@app.get(
    path="/items/{item_id}",
    status_code=status.HTTP_200_OK
)
def read_item(
    item_id: str = Path(...),
    response: Response = Response
):
    try:
        return items[item_id]
    except KeyError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail": "Item not found"}


@app.post(
    path="/items/",
    status_code=status.HTTP_201_CREATED
)
def create_item(
    item: Item = Body(...),
    response: Response = Response
):
    if item.id in items.keys():
        response.status_code = status.HTTP_409_CONFLICT
        return {
            "detail": "Item already exists",
            "item": item
        }
    items[item.id] = item
    return items[item.id]


@app.put(
    path="/items/{item_id}",
    status_code=status.HTTP_200_OK,
)
def update_item(
    item_id: str = Path(...),
    item: Item = Body(...),
    response: Response = Response
):
    if item_id in items.keys():
        items[item_id] = item
        return items[item_id]
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "detail": "Item not found",
            "item_id": item_id,
            "item": item
        }


@app.get(
    path="/items/",
    status_code=status.HTTP_200_OK
)
def get_item_by_price(
    price: float = Query(...),
    limit: int = Query(..., gt=0, le=100),
    response: Response = Response
):
    if price < 0 or limit < 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "detail": "Invalid query parameters",
            "price": price,
            "limit": limit
        }
    filter: List = [item for item in items.values() if item.price == price]
    return filter[:limit]