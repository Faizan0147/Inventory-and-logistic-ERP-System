from fastapi import APIRouter
from app.routes import (
    supplier,
    auth,
    admin,
    user,
    category,
    warehouse,
    product,
    inventory,
    invoice,
    invoice_items,
    purchase_order,
    poi,
    customers,
    shipments,
    langchain_chat,
    dashboard,
)
api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(supplier.router, prefix="/suppliers", tags=["Suppliers"])
api_router.include_router(category.router, prefix="/categories", tags=["Categories"])
api_router.include_router(warehouse.router, prefix="/warehouses", tags=["Warehouses"])
api_router.include_router(product.router, prefix="/products", tags=["Products"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(invoice.router, prefix="/invoice", tags=["Invoice"])
api_router.include_router(
    purchase_order.router, prefix="/purchase-order", tags=["purchaseOrder"]
)
api_router.include_router(poi.router, prefix="/poi", tags=["Purchase-Order-Items"])
api_router.include_router(user.router, prefix="/users", tags=["Users"])
api_router.include_router(
    invoice_items.router, prefix="/invoice-items", tags=["Invoice Items"]
)
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(shipments.router, prefix="/shipments", tags=["Shipments"])
api_router.include_router(langchain_chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
