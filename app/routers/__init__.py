from .users import router as users_router
from .items import router as items_router


routers = [
    users_router,
    items_router
]
