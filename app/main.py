from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.requests import Request

from app.database import create_pool, close_pool
from app.api import api_router
from app.mcp.server import mcp            # the FastMCP instance

BASE_DIR = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_pool()   # open connection pool on startup
    yield
    await close_pool()    # close pool on shutdown


app = FastAPI(
    title="Warehouse ERP API",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS — allow your frontend origin(s) to reach the API + MCP SSE ────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # restrict to your domain in production
    allow_credentials=True,        # allows cookies to be sent cross-origin
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.middleware("http")
async def auth_cookie_to_header(request: Request, call_next):
    # If Authorization header missing but cookie exists, copy cookie into header
    if "authorization" not in request.headers:
        token = request.cookies.get("access_token")
        if token:
            request.scope.setdefault("headers", [])
            request.scope["headers"].append(
                (b"authorization", f"Bearer {token}".encode())
            )
    return await call_next(request)


# ── Mount MCP server at /mcp (SSE transport) ────────────────────────
# Browser connects to:
#   GET  /mcp/sse       → SSE event stream
#   POST /mcp/messages  → send tool call messages
# The access_token cookie is sent automatically by the browser.
app.mount("/mcp", mcp.http_app(transport="sse"))


@app.get("/", tags=["Health"])
async def root():
    return {"message": "Warehouse ERP API is running"}


@app.get("/chat", include_in_schema=False)
async def chat_ui():
    return FileResponse(BASE_DIR / "chat_ui.html")

