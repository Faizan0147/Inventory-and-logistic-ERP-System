from fastapi import APIRouter
from app.routes import supplier, auth, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(supplier.router, prefix="/suppliers", tags=["Suppliers"])
