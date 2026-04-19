from fastapi import APIRouter
from app.routes import supplier, auth, admin, user, chat, langchain_chat

api_router = APIRouter()

# Keep application business routes (auth, admin, suppliers, users)
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(supplier.router, prefix="/suppliers", tags=["Suppliers"])
api_router.include_router(user.router, prefix="/users", tags=["Users"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(langchain_chat.router, prefix="/langchain-chat", tags=["LangChain Chat"])

# Include Gemini chatbot API
# api_router.include_router(chatbot.router)

# Include Groq Llama chatbot API
# api_router.include_router(groq_chat.router, prefix="/groq", tags=["Groq Chat"])