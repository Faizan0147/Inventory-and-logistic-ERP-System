from fastapi import APIRouter
from app.routes import customers, supplier, auth, admin, user, invoice_items, customers, shipments

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(supplier.router, prefix="/suppliers", tags=["Suppliers"])
api_router.include_router(user.router, prefix="/users", tags=["Users"])
api_router.include_router(invoice_items.router, prefix="/invoice-items", tags=["Invoice Items"])
api_router.include_router(customers.router,     prefix="/customers",     tags=["Customers"])
api_router.include_router(shipments.router,     prefix="/shipments",     tags=["Shipments"])
