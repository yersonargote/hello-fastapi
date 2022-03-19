from typing import Optional
from fastapi import FastAPI, status, Response
from pydantic import BaseModel
from typing import List, Dict


app = FastAPI()


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


class ItemOut(Item):
    id: str


items: Dict[str, Item] = {}


@app.get(
    "/items",
    status_code=status.HTTP_200_OK
)
def read_all_items():
    return items


@app.get(
    "/items/{item_id}",
    status_code=status.HTTP_200_OK
)
def read_item(item_id: str, response: Response = Response):
    try:
        return items[item_id]
    except KeyError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail": "Item not found"}


@app.post(
    "/items/{item_id}",
    status_code=status.HTTP_201_CREATED
)
def create_item(item_id: str, item: Item, response: Response = Response):
    if item_id in items.keys():
        response.status_code = status.HTTP_409_CONFLICT
        return {
            "detail": "Item already exists",
            "item_id": item_id,
            "item": item
        }
    items[item_id] = item
    return items[item_id]


@app.put(
    "/items/{item_id}",
    status_code=status.HTTP_200_OK
)
def update_item(item_id: str, item: Item, response: Response = Response):
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
