from fastapi import APIRouter
from app.api.v1.endpoints import cart

api_router = APIRouter()
api_router.include_router(cart.router)
