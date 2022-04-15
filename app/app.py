# From fastapi
from fastapi.applications import FastAPI
# From tortoise
from tortoise.contrib.fastapi import register_tortoise
# From local
from app.config import TORTOISE_ORM
from app.routers import routers

app = FastAPI()


for router in routers:
    app.include_router(router)


register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True
)
