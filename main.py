from typing import List, Optional
from fastapi import Body, FastAPI, Path, Query, status, HTTPException
from pydantic import BaseModel, Field
from typing import Dict


app = FastAPI()


class Item(BaseModel):
    id: str = Field(..., title="The item's unique ID")
    name: str = Field(..., min_length=2, max_length=50,
                      title="The item's name")
    description: Optional[str] = Field(
        None, min_length=3, max_length=500, title="The item's description")
    price: float = Field(..., gt=0, le=100000000, title="The item's price")
    stock: int = Field(..., gt=0, le=100, title="The item's stock")


items: Dict[str, Item] = {}


@app.get(
    path="/items",
    status_code=status.HTTP_200_OK,
    response_model=List[Item],
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
