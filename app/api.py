from fastapi import APIRouter
from app.routes import auth, admin, langchain_chat

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(langchain_chat.router, prefix="/chat", tags=["Chat"])
