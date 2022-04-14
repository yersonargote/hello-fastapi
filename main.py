
from fastapi.applications import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from config import TORTOISE_ORM
from routers import routers

app = FastAPI()


for router in routers:
    app.include_router(router)


register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True
)
