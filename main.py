from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


items: Dict[str, Item] = {}


@app.get("/items")
def read_root():
    return items

@app.get("/items/{item_id}")
def read_item(item_id: str):
    return items[item_id]

@app.post("/items/{item_id}")
def create_item(item_id: str, item: Item):
    if item is None:
        return {"error": "Item not found"}
    items[item_id] = item
    return item

@app.put("/items/{item_id}")
def update_item(item_id: str, item: Item):
    if item is None:
        return {"error": "item not found"}
    items[item_id] = item
    return item