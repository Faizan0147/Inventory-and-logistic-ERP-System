from fastapi import APIRouter
from app.api.v1.endpoints import supplier, supplierbankdetails

api_router = APIRouter()

api_router.include_router(supplier.router, prefix="/suppliers", tags=["Suppliers"])
api_router.include_router(supplierbankdetails.router, prefix="/suppliers", tags=["Supplier Bank Details"])
